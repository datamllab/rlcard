'''
    File name: rlcard/games/bauernskat/sac_agent/model.py
    Author: Oliver Czerwinski
    Date created: 11/10/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import torch
import torch.nn as nn
from typing import Dict, Tuple
from torch.nn.utils.rnn import pack_padded_sequence, pad_packed_sequence

from rlcard.agents.bauernskat.sac_agent.config import BauernskatNetConfig

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
        
        return self.mlp(pooled)

class BauernskatNet(nn.Module):
    """
    SAC Network for Bauernskat.
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
        self.unaccounted_mask_processor = self._build_mlp(32, list(config.mask_processor_hidden_dims), config.branch_output_dim)
        self.trick_processor = CardSetProcessor(*card_set_args)
        self.cemetery_processor = CardSetProcessor(*card_set_args)

        self.indicator_processor = self._build_mlp(config.indicator_vector_dim, list(config.indicator_mlp_dims), config.branch_output_dim)
        self.context_processor = self._build_mlp(config.context_vector_dim, list(config.mlp_hidden_dims), config.branch_output_dim)

        lstm_out_dim = config.lstm_hidden_dim * (2 if config.use_bidirectional else 1)
        self.lstm = nn.LSTM(config.action_history_frame_size, config.lstm_hidden_dim, config.num_lstm_layers,
                            bidirectional=config.use_bidirectional, batch_first=True)
        
        self.attn = nn.MultiheadAttention(lstm_out_dim, config.attn_heads, batch_first=True) if config.use_attention else None
        self.history_processor = self._build_mlp(lstm_out_dim, list(config.lstm_fc_dims), config.branch_output_dim)
        
        self.action_card_processor = CardSetProcessor(*card_set_args)
        self.trump_action_processor = nn.Sequential(
            nn.Linear(config.card_embedding_dim, config.branch_output_dim),
            nn.GELU(),
            nn.LayerNorm(config.branch_output_dim)
        )

        # SAC Heads
        concat_dim = config.branch_output_dim * 8 
        
        head_input_dim = concat_dim + config.branch_output_dim

        def build_head():
            layers = []
            dims = [head_input_dim] + list(config.head_hidden_dims)
            for i in range(len(config.head_hidden_dims)):
                layers.extend([
                    nn.Linear(dims[i], dims[i+1]),
                    ResidualBlock(dims[i+1]),
                    nn.GELU()
                ])
            layers.append(nn.Linear(dims[-1], 1))
            return nn.Sequential(*layers)

        self.actor_head = build_head()
        self.critic1_head = build_head()
        self.critic2_head = build_head()
        
        self.register_buffer('all_actions_indices', torch.arange(38, dtype=torch.long))

    @staticmethod
    def _build_mlp(input_dim, hidden_dims, output_dim):
        """
        Creates an MLP with specific dimensions.
        """
        
        layers = []
        curr = input_dim
        for h in hidden_dims:
            layers.extend([nn.Linear(curr, h), nn.GELU()])
            curr = h
        layers.append(nn.Linear(curr, output_dim))
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
            b_non, s_non, _ = lstm_out.shape
            indices = torch.arange(s_non, device=x.device).expand(b_non, -1)
            attn_mask = indices >= non_empty_lengths.unsqueeze(1)
            last_seq_idxs = (non_empty_lengths - 1).clamp(min=0)
            query = lstm_out[torch.arange(b_non), last_seq_idxs, :].unsqueeze(1)
            attn_out, _ = self.attn(query=query, key=lstm_out, value=lstm_out, key_padding_mask=attn_mask)
            summary = attn_out.squeeze(1)
        else:
            b_non = lstm_out.shape[0]
            last_seq_idxs = (non_empty_lengths - 1).clamp(min=0)
            summary = lstm_out[torch.arange(b_non), last_seq_idxs, :]
        
        processed = self.history_processor(summary)
        full_batch_summary.index_add_(0, non_empty_indices, processed)
        
        return full_batch_summary

    def encode_state(self, state_obs: Dict[str, torch.Tensor]) -> torch.Tensor:
        """
        Encodes the state observation into a fixed-size vector.
        """
        
        my_layout = self.my_layout_processor(state_obs['my_layout_tensor'])
        opp_layout = self.opponent_layout_processor(state_obs['opponent_layout_tensor'])
        mask_vec = self.unaccounted_mask_processor(state_obs['unaccounted_cards_mask'])
        trick = self.trick_processor(state_obs['trick_card_ids'], state_obs['trick_card_ids'] != -1)
        cemetery = self.cemetery_processor(state_obs['cemetery_card_ids'], state_obs['cemetery_card_ids'] != -1)
        
        my_ind = self.indicator_processor(state_obs['my_hidden_indicators'])
        opp_ind = self.indicator_processor(state_obs['opponent_hidden_indicators'])
        indicator = my_ind + opp_ind
        
        ctx = self.context_processor(state_obs['context'])
        hist = self._forward_history(state_obs['action_history'])

        return torch.cat([my_layout, opp_layout, mask_vec, trick, cemetery, indicator, ctx, hist], dim=-1)

    def _process_all_actions(self):
        """ 
        Processes all 38 actions into embeddings.
        """
        
        # Card Actions
        card_indices = torch.arange(32, device=self.all_actions_indices.device).unsqueeze(1)
        card_vecs = self.action_card_processor(card_indices, torch.ones_like(card_indices, dtype=torch.bool))
        
        # Trump Actions
        trump_indices = torch.arange(6, device=self.all_actions_indices.device).unsqueeze(1)
        trump_embs = self.trump_action_embedding(trump_indices)
        trump_vecs = self.trump_action_processor(trump_embs.squeeze(1))
        
        return torch.cat([card_vecs, trump_vecs], dim=0)

    def evaluate_all_actions(self, state_obs: Dict[str, torch.Tensor]) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Evaluates all possible actions for the given state.
        """
        
        batch_size = state_obs['context'].shape[0]
        state_vec = self.encode_state(state_obs)
        
        action_vecs = self._process_all_actions()
        
        state_expanded = state_vec.unsqueeze(1).expand(-1, 38, -1)
        action_expanded = action_vecs.unsqueeze(0).expand(batch_size, -1, -1)
        
        fused = torch.cat([state_expanded, action_expanded], dim=-1)
        
        logits = self.actor_head(fused).squeeze(-1)
        q1 = self.critic1_head(fused).squeeze(-1)
        q2 = self.critic2_head(fused).squeeze(-1)
        
        return logits, q1, q2