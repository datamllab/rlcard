'''
    File name: rlcard/games/bauernskat/sac_agent/agent.py
    Author: Oliver Czerwinski
    Date created: 11/10/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import random
from collections import Counter
from typing import Dict, Tuple, List, Optional

import numpy as np
import torch
import torch.nn.functional as F
from torch.distributions import Categorical
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

from rlcard.envs.env import Env
from rlcard.games.bauernskat.action_event import ActionEvent, DeclareTrumpAction
from rlcard.games.bauernskat.card import BauernskatCard
from rlcard.agents.bauernskat import rule_agents as bauernskat_rule_agents

from rlcard.agents.bauernskat.sac_agent.model import BauernskatNet
from rlcard.agents.bauernskat.sac_agent.config import BauernskatNetConfig, TrainerConfig

class SACEstimator:
    """
    Soft Actor-Critic estimator with Actor and Twin Critics.
    """
    def __init__(self, net_config: BauernskatNetConfig, train_config: TrainerConfig, device: torch.device):
        self.device = device
        self.gamma = train_config.gamma
        self.tau = train_config.tau
        
        self.net = BauernskatNet(net_config).to(device)
        self.target_net = BauernskatNet(net_config).to(device)
        self.target_net.load_state_dict(self.net.state_dict())
        self.target_net.eval()
        
        self.optimizer = torch.optim.AdamW(
            self.net.parameters(), 
            lr=train_config.critic_lr,
            weight_decay=train_config.weight_decay
        )

        self.use_scheduler = train_config.use_lr_scheduler
        if self.use_scheduler:
            t0_steps = max(1, int(train_config.cosine_T0 / train_config.batch_size))
            
            self.scheduler = CosineAnnealingWarmRestarts(
                self.optimizer,
                T_0=t0_steps,
                T_mult=train_config.cosine_T_mult,
                eta_min=train_config.cosine_eta_min
            )

        self.learn_alpha = train_config.learn_alpha
        self.target_entropy = -np.log(1.0 / 8.0) * train_config.target_entropy_ratio
        
        if self.learn_alpha:
            self.log_alpha = torch.zeros(1, requires_grad=True, device=device)
            self.alpha_optim = torch.optim.Adam([self.log_alpha], lr=train_config.alpha_lr)
            self.alpha = self.log_alpha.exp()
        else:
            self.alpha = torch.tensor(train_config.initial_alpha).to(device)

    def train_step(self, batch: dict, clip_norm: float) -> Tuple[float, float, float, float, float]:
        """
        Performs a training step using a batch of transitions.
        """
        
        # Batch Tensors
        states = batch.get('observation').to(self.device)
        actions = batch.get('action').long().to(self.device)
        rewards = batch.get(('next', 'reward')).to(self.device)
        dones = batch.get(('next', 'done')).float().to(self.device)
        next_states = batch.get(('next', 'observation')).to(self.device)
        masks = batch.get('legal_actions_mask').bool().to(self.device)
        next_masks = batch.get(('next', 'legal_actions_mask')).bool().to(self.device)

        logits, q1_all, q2_all = self.net.evaluate_all_actions(states)
        
        # Q-Values
        q1_pred = q1_all.gather(1, actions)
        q2_pred = q2_all.gather(1, actions)
        
        # Target Q-Values
        with torch.no_grad():
            next_logits, next_q1, next_q2 = self.target_net.evaluate_all_actions(next_states)
            
            next_logits[~next_masks] = -1e8
            next_probs = F.softmax(next_logits, dim=-1)
            next_log_probs = F.log_softmax(next_logits, dim=-1)
            
            min_next_q = torch.min(next_q1, next_q2)
            
            target_v = torch.sum(next_probs * (min_next_q - self.alpha * next_log_probs), dim=-1, keepdim=True)
            target_q = rewards + (1 - dones) * self.gamma * target_v

        critic_loss = F.mse_loss(q1_pred, target_q) + F.mse_loss(q2_pred, target_q)

        q1_detach = q1_all.detach()
        q2_detach = q2_all.detach()
        min_q = torch.min(q1_detach, q2_detach)
        
        logits[~masks] = -1e8
        probs = F.softmax(logits, dim=-1)
        log_probs = F.log_softmax(logits, dim=-1)
        
        actor_loss = torch.sum(probs * (self.alpha * log_probs - min_q), dim=-1).mean()

        alpha_loss = 0.0
        curr_alpha = self.alpha.item() if isinstance(self.alpha, torch.Tensor) else self.alpha
        
        # Update Entropy Temperature
        if self.learn_alpha:
            with torch.no_grad():
                entropy = -torch.sum(probs * log_probs, dim=-1).mean()
            
            alpha_loss = -(self.log_alpha * (entropy - self.target_entropy).detach())
            
            self.alpha_optim.zero_grad()
            alpha_loss.backward()
            self.alpha_optim.step()
            
            self.alpha = self.log_alpha.exp()
            curr_alpha = self.alpha.item()

        # Update Netoworks
        total_loss = critic_loss + actor_loss
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.net.parameters(), clip_norm)
        self.optimizer.step()

        current_lr = self.optimizer.param_groups[0]['lr']
        if self.use_scheduler:
            self.scheduler.step()
            current_lr = self.scheduler.get_last_lr()[0]

        return critic_loss.item(), actor_loss.item(), curr_alpha, q1_pred.mean().item(), current_lr

    def update_target_net(self):
        """
        Soft-update for the target network.
        """
        
        with torch.no_grad():
            for param, target_param in zip(self.net.parameters(), self.target_net.parameters()):
                target_param.data.copy_(self.tau * param.data + (1 - self.tau) * target_param.data)


class AgentSAC_Actor:
    """ 
    An agent that uses a Soft Actor-Critic network for decision making.
    """
    
    def __init__(self, net: BauernskatNet, device: str = 'cpu', use_teacher: bool = False):
        """
        Initializes AgentSAC_Actor.
        """
        
        self.net = net
        self.device = device
        
        self.teacher = bauernskat_rule_agents.BauernskatLookaheadRuleAgent() if use_teacher else None

    @staticmethod
    def _map_action_to_sac_idx(action_id: int) -> int:
        """
        Maps action_id to SAC index.
        """
        
        if action_id < 5: return 32 + action_id
        else: return action_id - 5

    @staticmethod
    def _map_sac_idx_to_action(idx: int) -> int:
        """
        Maps SAC index back to action_id.
        """
        
        if idx >= 32: return idx - 32
        else: return idx + 5

    def _get_rule_based_trump_action(self, state: dict) -> Optional[int]:
        """
        Heuristic for trump selection:
        - If 2 or more Jacks: Declare Grand ('G')
        - Else: Suit with most cards.
        - Otherwise: Suit with highest rank card.
        """
        
        legal_action_ids = list(state['legal_actions'].keys())
        raw_info = state.get('raw_state_info')
        if not raw_info: return None

        my_cards = raw_info.get('my_cards', [])
        if not my_cards: return random.choice(legal_action_ids)

        # Jacks
        num_jacks = sum(1 for card in my_cards if card.rank == 'J')
        if num_jacks >= 2:
            for action_id in legal_action_ids:
                action = ActionEvent.from_action_id(action_id)
                if isinstance(action, DeclareTrumpAction) and action.trump_suit == 'G':
                    return action_id
        
        # Suit counts
        suit_counts = Counter(card.suit for card in my_cards)
        if not suit_counts:
            return random.choice(legal_action_ids)

        max_count = max(suit_counts.values())
        best_suits = [suit for suit, count in suit_counts.items() if count == max_count]

        # Highest rank suit card
        if len(best_suits) == 1:
            best_suit_choice = best_suits[0]
        else:
            best_rank_val = -1
            
            rank_order = BauernskatCard.ranks 
            best_suit_choice = best_suits[0]
            
            for suit in best_suits:
                cards_of_suit = [card for card in my_cards if card.suit == suit]
                if cards_of_suit:
                    max_rank_in_suit = max(rank_order.index(c.rank) for c in cards_of_suit)
                    if max_rank_in_suit > best_rank_val:
                        best_rank_val = max_rank_in_suit
                        best_suit_choice = suit
        
        for action_id in legal_action_ids:
            action = ActionEvent.from_action_id(action_id)
            if isinstance(action, DeclareTrumpAction) and action.trump_suit == best_suit_choice:
                return action_id
        
        return random.choice(legal_action_ids)

    def step(self, state: dict, env: Env, trump_rule_prob: float = 0.0, teacher_epsilon: float = 0.0) -> Tuple[int, List[int]]:
        """ 
        Chooses an action based on SAC policy.
        """
        
        legal_actions = list(state['legal_actions'].keys())
        if not legal_actions:
            return -1, []

        r = random.random()

        # Teacher Forcing
        if self.teacher is not None and r < teacher_epsilon:
            action = self.teacher.step(state)
            return action, legal_actions
        
        # 2. Rule-Based Trump Selection
        if trump_rule_prob > 0.0:
            raw_info = state.get('raw_state_info')
            if raw_info and raw_info.get('round_phase') == 'declare_trump':
                if random.random() < trump_rule_prob:
                    action = self._get_rule_based_trump_action(state)
                    if action is not None:
                        return action, legal_actions

        # 3. SAC Policy
        legal_indices = [self._map_action_to_sac_idx(a) for a in legal_actions]
        
        mask = torch.zeros(38, dtype=torch.bool)
        mask[legal_indices] = True
        
        with torch.no_grad():
            state_batch = {k: torch.from_numpy(np.array(v)).unsqueeze(0).to(self.device) 
                        for k, v in state['obs'].items()}
            
            logits, _, _ = self.net.evaluate_all_actions(state_batch)
            logits = logits.squeeze(0).cpu()
            
            logits[~mask] = -float('inf')
            
            probs = F.softmax(logits, dim=-1)
            dist = Categorical(probs)
            sac_idx = dist.sample().item()

        return self._map_sac_idx_to_action(sac_idx), legal_actions

    def eval_step(self, state: dict, env: Env) -> Tuple[int, Dict]:
        """ 
        Chooses the best action without exploration.
        """
        
        legal_actions = list(state['legal_actions'].keys())
        legal_indices = [self._map_action_to_sac_idx(a) for a in legal_actions]
        
        mask = torch.zeros(38, dtype=torch.bool)
        mask[legal_indices] = True
        
        with torch.no_grad():
            state_batch = {k: torch.from_numpy(np.array(v)).unsqueeze(0).to(self.device) 
                        for k, v in state['obs'].items()}
            
            logits, _, _ = self.net.evaluate_all_actions(state_batch)
            logits = logits.squeeze(0).cpu()
            
            logits[~mask] = -float('inf')
            
            sac_idx = torch.argmax(logits).item()
            
        return self._map_sac_idx_to_action(sac_idx), {}