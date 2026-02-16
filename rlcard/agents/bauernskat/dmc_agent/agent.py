'''
    File name: rlcard/games/bauernskat/dmc_agent/agent.py
    Author: Oliver Czerwinski
    Date created: 08/13/2025
    Date last modified: 12/26/2025
    Python Version: 3.9+
'''

import random
from collections import Counter
from typing import Dict, Tuple, List, Optional

import numpy as np
import torch
import torch.nn.functional as F
from torch.optim.lr_scheduler import CosineAnnealingWarmRestarts

from rlcard.envs.env import Env
from rlcard.games.bauernskat.action_event import ActionEvent, DeclareTrumpAction
from rlcard.games.bauernskat.card import BauernskatCard
from rlcard.agents.bauernskat import rule_agents as bauernskat_rule_agents

from rlcard.agents.bauernskat.dmc_agent.model import BauernskatNet
from rlcard.agents.bauernskat.dmc_agent.config import BauernskatNetConfig

class Estimator:
    """
    Q-value estimator using a neural network.
    """
    
    def __init__(self, net_config: BauernskatNetConfig, learning_rate: float, lr_gamma: float, device: torch.device, weight_decay: float = 1e-6, cosine_T0: int = 51_200_000, cosine_T_mult: int = 2, cosine_eta_min: float = 3e-6):
        """
        Initializes Estimator.
        """
        
        self.device = device
        self.qnet = BauernskatNet(net_config).to(device)
            
        self.optimizer = torch.optim.AdamW(self.qnet.parameters(), lr=learning_rate, weight_decay=weight_decay)
        
        self.scheduler = CosineAnnealingWarmRestarts(
            self.optimizer, 
            T_0=cosine_T0,
            T_mult=cosine_T_mult,
            eta_min=cosine_eta_min
        )

    def train_step(self, states: dict, actions: dict, targets: torch.Tensor, clip_norm: float) -> float:
        """
        Performs a training step on a batch of state-action pairs and targets.
        """
        
        self.qnet.train()
        predicted_q_values = self.qnet(states, actions)
        
        loss = F.mse_loss(predicted_q_values, targets)
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.qnet.parameters(), clip_norm)
        self.optimizer.step()
        self.scheduler.step()
        return loss.item()

    def predict_nograd(self, states: dict, actions: dict) -> torch.Tensor:
        """
        Predicts Q-values for a batch of state-action pairs without gradient updates.
        """
        
        self.qnet.eval()
        with torch.no_grad():
            return self.qnet(states, actions)


class AgentDMC_Actor:
    """
    An agent that uses an action-in Q-value network for decision making.
    """
    
    def __init__(self, net: BauernskatNet, device: str = 'cpu', use_teacher: bool = False):
        """
        Initializes AgentDMC_Actor.
        """
        
        self.use_raw = True
        self.net = net
        self.device = device
        
        # Optional teacher
        self.teacher = bauernskat_rule_agents.BauernskatLookaheadRuleAgent() if use_teacher else None

    @staticmethod
    def _get_action_obs(action_id: int) -> Dict[str, List[int]]:
        """
        Creates an action_obs dictionary for a given action_id.
        """
        
        if action_id >= 5:
            return {'action_card_ids': [action_id - 5], 'trump_action_id': [-1]}
        else:
            return {'action_card_ids': [-1], 'trump_action_id': [action_id]}

    def _get_best_action(self, state: dict, env: Env) -> int:
        """
        Encodes all legal actions at once and selects the one with the highest Q-value.
        """
        legal_actions = list(state['legal_actions'].keys())
        if not legal_actions:
            return -1

        with torch.no_grad():
            state_batch = {k: torch.from_numpy(np.array(v)).unsqueeze(0).to(self.device) 
                        for k, v in state['obs'].items()}
            
            state_encoding = self.net.encode_state(state_batch)

            action_obs_list = [self._get_action_obs(a) for a in legal_actions]
            card_ids = [ao['action_card_ids'] for ao in action_obs_list]
            trump_ids = [ao['trump_action_id'] for ao in action_obs_list]
            action_batch = {
                'action_card_ids': torch.LongTensor(card_ids).to(self.device),
                'trump_action_id': torch.LongTensor(trump_ids).to(self.device)
            }

            repeated_state_encoding = state_encoding.repeat(len(legal_actions), 1)

            q_values = self.net.predict_q(repeated_state_encoding, action_batch).cpu().numpy()

        return legal_actions[np.argmax(q_values)]

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

    def step(self, state: dict, env: Env, epsilon: float = 0.0, trump_rule_prob: float = 0.0, teacher_epsilon: float = 0.0) -> Tuple[int, Dict]:
        """ 
        Chooses an action based on epsilon-greedy strategy with optional teacher forcing and rule-based trump selection.
        """
        
        r = random.random()

        # Teacher Forcing
        if self.teacher is not None and r < teacher_epsilon:
            action = self.teacher.step(state)
            action_obs = self._get_action_obs(action)
            return action, action_obs
        
        # Rule-Based Trump Selection
        if trump_rule_prob > 0.0:
            raw_info = state.get('raw_state_info')
            if raw_info and raw_info.get('round_phase') == 'declare_trump':
                if random.random() < trump_rule_prob:
                    action = self._get_rule_based_trump_action(state)
                    if action is not None:
                        action_obs = self._get_action_obs(action)
                        return action, action_obs

        # Random Exploration
        if r < epsilon:
            action = random.choice(list(state['legal_actions'].keys()))
        else:
            # Greedy
            action = self._get_best_action(state, env)
        
        action_obs = self._get_action_obs(action)
        return action, action_obs

    def eval_step(self, state: dict, env: Env) -> Tuple[int, Dict]:
        """
        Chooses the best action without exploration.
        """
        with torch.no_grad():
            action, _ = self.step(state, env, epsilon=0.0, trump_rule_prob=0.0, teacher_epsilon=0.0)
        
        return action, {}