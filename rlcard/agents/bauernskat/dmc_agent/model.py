'''
    File name: rlcard/games/bauernskat/dmc_agent/model.py
    Author: Oliver Czerwinski
    Date created: 08/13/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import torch
import torch.nn as nn
from typing import Dict, List
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from rlcard.agents.bauernskat.dmc_agent.config import BauernskatNetConfig


class ResidualBlock(nn.Module):
    """
    Basic residual block.
    """
    
    def __init__(self, dim: int):
        """
        Initializes ResidualBlock.
        """
        
        super().__init__()
        self.layers = nn.Sequential(
            nn.LayerNorm(dim),
            nn.Linear(dim, dim * 4),
            nn.GELU(),
            nn.Linear(dim * 4, dim)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Outputs the result of the residual block.
        """
        
        return x + self.layers(x)


class LayoutProcessor(nn.Module):
    """
    Processes a (8, 2) layout tensor.
    """
    
    def __init__(self, shared_card_embedding: nn.Embedding, output_dim: int, hidden_dim: int):
        """
        Initializes LayoutProcessor.
        """
        
        super().__init__()
        self.embedding = shared_card_embedding
        embedding_dim = self.embedding.embedding_dim
        
        input_size = 8 * 2 * embedding_dim
        self.mlp = nn.Sequential(
            nn.Linear(input_size, hidden_dim),
            nn.GELU(),
            nn.LayerNorm(hidden_dim),
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, layout_tensor: torch.Tensor) -> torch.Tensor:
        """
        Outputs an embedding for the layout tensor.
        """
        
        embedded = self.embedding(layout_tensor)
        flattened = embedded.view(embedded.shape[0], -1)
        return self.mlp(flattened)


class CardSetProcessor(nn.Module):
    """
    Processes a flexible sized set of cards.
    """
    def __init__(self, shared_card_embedding: nn.Embedding, output_dim: int, pool_type: str = 'mean'):
        """
        Initializes CardSetProcessor.
        """
        
        super().__init__()
        self.embedding = shared_card_embedding
        self.pool_type = pool_type
        self.padding_idx = shared_card_embedding.padding_idx
        
        self.mlp = nn.Sequential(
            nn.Linear(self.embedding.embedding_dim, output_dim),
            nn.GELU(),
            nn.LayerNorm(output_dim)
        )

    def forward(self, ids: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
        """
        Outputs an embedding for the set of cards.
        """
        
        if ids.shape[1] == 0:
            return torch.zeros(ids.shape[0], self.mlp[0].out_features, device=ids.device)

        safe_ids = ids.clone()
        if self.padding_idx is not None:
            safe_ids[ids == -1] = self.padding_idx
        
        embedded = self.embedding(safe_ids)

        if self.pool_type == 'mean':
            num_cards = mask.sum(dim=1, keepdim=True).clamp(min=1)
            pooled = embedded.sum(dim=1) / num_cards
        elif self.pool_type == 'sum':
            pooled = embedded.sum(dim=1)
        else:
            raise ValueError(f"Unknown pool_type: {self.pool_type}")
            
        return self.mlp(pooled)


class BauernskatNet(nn.Module):
    """
    Action-in Q-network for Bauernskat.
    """
    
    def __init__(self, config: BauernskatNetConfig):
        """
        Initializes BauernskatNet.
        """
        
        super().__init__()
        self.config = config

        self.card_embedding = nn.Embedding(33, config.card_embedding_dim, padding_idx=32)
        self.trump_action_embedding = nn.Embedding(6, config.card_embedding_dim, padding_idx=5)

        card_set_args = (self.card_embedding, config.branch_output_dim, config.pool_type)
        layout_proc_args = (self.card_embedding, config.branch_output_dim, config.layout_processor_hidden_dim)
        
        self.my_layout_processor = LayoutProcessor(*layout_proc_args)
        self.opponent_layout_processor = LayoutProcessor(*layout_proc_args)
        self.unaccounted_mask_processor = self._build_mlp(
            input_dim=32,
            hidden_dims=list(config.mask_processor_hidden_dims),
            output_dim=config.branch_output_dim
        )
        self.trick_processor = CardSetProcessor(*card_set_args)
        self.cemetery_processor = CardSetProcessor(*card_set_args)

        self.indicator_processor = self._build_mlp(
            input_dim=config.indicator_vector_dim,
            hidden_dims=list(config.indicator_mlp_dims),
            output_dim=config.branch_output_dim
        )
        
        self.context_processor = self._build_mlp(
            input_dim=config.context_vector_dim,
            hidden_dims=list(config.mlp_hidden_dims),
            output_dim=config.branch_output_dim
        )

        lstm_out_dim = config.lstm_hidden_dim * (2 if config.use_bidirectional else 1)
        self.lstm = nn.LSTM(config.action_history_frame_size, config.lstm_hidden_dim, config.num_lstm_layers,
                            bidirectional=config.use_bidirectional, batch_first=True)
        self.attn = nn.MultiheadAttention(lstm_out_dim, config.attn_heads, batch_first=True) if config.use_attention else None
        
        self.history_processor = self._build_mlp(
            input_dim=lstm_out_dim,
            hidden_dims=list(config.lstm_fc_dims),
            output_dim=config.branch_output_dim
        )
        
        self.action_card_processor = CardSetProcessor(*card_set_args)
        self.trump_action_processor = nn.Sequential(
            nn.Linear(config.card_embedding_dim, config.branch_output_dim),
            nn.GELU(),
            nn.LayerNorm(config.branch_output_dim)
        )
        
        concat_dim = config.branch_output_dim * 9
        head_layers = []
        all_dims = [concat_dim] + list(config.head_hidden_dims)
        
        for i in range(len(config.head_hidden_dims)):
            head_layers.extend([
                nn.Linear(all_dims[i], all_dims[i+1]),
                ResidualBlock(all_dims[i+1]),
                nn.Dropout(p=config.head_dropout)
            ])
            
        head_layers.extend([
            nn.LayerNorm(config.head_hidden_dims[-1]),
            nn.GELU(),
            nn.Linear(config.head_hidden_dims[-1], 1)
        ])
        self.head = nn.Sequential(*head_layers)
        
    @staticmethod
    def _build_mlp(input_dim: int, hidden_dims: List[int], output_dim: int) -> nn.Sequential:
        """
        Creates an MLP with specific dimensions.
        """
        
        layers = []
        current_dim = input_dim
        for hidden_dim in hidden_dims:
            layers.extend([nn.Linear(current_dim, hidden_dim), nn.GELU()])
            current_dim = hidden_dim
        layers.append(nn.Linear(current_dim, output_dim))
        return nn.Sequential(*layers)

    def _forward_history(self, x: torch.Tensor) -> torch.Tensor:
        """
        Processes the action history using LSTM and attention.
        """
        
        B, _, _ = x.shape
        lengths = torch.sum(x.abs().sum(dim=-1) > 0, dim=-1)
        full_batch_summary = torch.zeros(B, self.config.branch_output_dim, device=x.device)

        non_empty_mask = lengths > 0
        if not non_empty_mask.any():
            return full_batch_summary

        non_empty_x = x[non_empty_mask]
        non_empty_lengths = lengths[non_empty_mask]
        non_empty_indices = non_empty_mask.nonzero(as_tuple=True)[0]

        sorted_lengths, sorted_indices = torch.sort(non_empty_lengths, descending=True)
        sorted_x = non_empty_x.index_select(0, sorted_indices)
        
        packed_input = pack_padded_sequence(sorted_x, sorted_lengths.cpu(), batch_first=True, enforce_sorted=True)
        packed_output, _ = self.lstm(packed_input)
        lstm_out, _ = pad_packed_sequence(packed_output, batch_first=True, total_length=sorted_x.size(1))

        _, unsorted_indices = torch.sort(sorted_indices)
        lstm_out = lstm_out.index_select(0, unsorted_indices)
        
        if self.attn:
            b_non_empty, s_non_empty, _ = lstm_out.shape
            indices = torch.arange(s_non_empty, device=x.device).expand(b_non_empty, -1)
            attn_mask = indices >= non_empty_lengths.unsqueeze(1)
            last_seq_idxs = (non_empty_lengths - 1).clamp(min=0)
            query = lstm_out[torch.arange(b_non_empty), last_seq_idxs, :].unsqueeze(1)
            attn_out, _ = self.attn(query=query, key=lstm_out, value=lstm_out, key_padding_mask=attn_mask)
            summary = attn_out.squeeze(1)
        else:
            b_non_empty = lstm_out.shape[0]
            last_seq_idxs = (non_empty_lengths - 1).clamp(min=0)
            summary = lstm_out[torch.arange(b_non_empty), last_seq_idxs, :]

        processed_summary = self.history_processor(summary)
        full_batch_summary.index_add_(0, non_empty_indices, processed_summary)

        return full_batch_summary

    def encode_state(self, state_obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Encodes the state observation into a fixed-size vector.
        """
        
        my_layout_vec = self.my_layout_processor(state_obs['my_layout_tensor'])
        opp_layout_vec = self.opponent_layout_processor(state_obs['opponent_layout_tensor'])
        unaccounted_mask_vec = self.unaccounted_mask_processor(state_obs['unaccounted_cards_mask'])
        trick_vec = self.trick_processor(state_obs['trick_card_ids'], state_obs['trick_card_ids'] != -1)
        cemetery_vec = self.cemetery_processor(state_obs['cemetery_card_ids'], state_obs['cemetery_card_ids'] != -1)

        my_hidden_vec = self.indicator_processor(state_obs['my_hidden_indicators'])
        opp_hidden_vec = self.indicator_processor(state_obs['opponent_hidden_indicators'])
        indicator_vec = my_hidden_vec + opp_hidden_vec

        context_vec = self.context_processor(state_obs['context'])
        history_vec = self._forward_history(state_obs['action_history'])

        state_encoding = torch.cat([
            my_layout_vec, opp_layout_vec, unaccounted_mask_vec,
            trick_vec, cemetery_vec,
            indicator_vec, context_vec, history_vec
        ], dim=-1)
        
        return state_encoding

    def predict_q(self, state_encoding: torch.Tensor, action_obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Predicts Q-values for given state encodings and actions.
        """
        
        action_cards_vec = self.action_card_processor(action_obs['action_card_ids'], action_obs['action_card_ids'] != -1)
        
        trump_action_id = action_obs['trump_action_id']
        safe_trump_id = trump_action_id.clone()
        safe_trump_id[trump_action_id == -1] = self.trump_action_embedding.padding_idx
        trump_action_embedded = self.trump_action_embedding(safe_trump_id)
        processed_trump_vec = self.trump_action_processor(trump_action_embedded.squeeze(1))

        is_card_play_action = (action_obs['action_card_ids'][:, 0] != -1).unsqueeze(-1).float()
        is_trump_action = (action_obs['trump_action_id'][:, 0] != -1).unsqueeze(-1).float()
        
        masked_card_vec = action_cards_vec * is_card_play_action
        masked_trump_vec = processed_trump_vec * is_trump_action
        action_vec = masked_card_vec + masked_trump_vec

        fused = torch.cat([state_encoding, action_vec], dim=-1)
        q_value = self.head(fused).squeeze(-1)
        
        return q_value

    def forward(self, state_obs: Dict[str, torch.Tensor], action_obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Forward pass to get Q-values.
        """
        
        state_encoding = self.encode_state(state_obs)
        return self.predict_q(state_encoding, action_obs)