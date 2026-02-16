'''
    File name: rlcard/envs/bauernskat.py
    Author: Oliver Czerwinski
    Date created: 08/02/2025
    Date last modified: 25/12/2025
    Python Version: 3.9+
'''

import copy
import numpy as np

from rlcard.envs import Env
from rlcard.games.bauernskat.game import BauernskatGame as Game
from rlcard.games.bauernskat.action_event import ActionEvent, DeclareTrumpAction
from rlcard.games.bauernskat import config


class BauernskatEnv(Env):
    """
    Bauernskat Environment wrapper for RLCard.
    """

    def __init__(self, config=None):
        """
        Inititialized BauernskatEnv.
        """
        
        if config is None:
            config = {}
        self.name = 'bauernskat'
        self.game = Game(information_level=config.get('information_level', 'normal'))
        super().__init__(config)
        
        self.state_shape = {} 
        self.action_shape = [None for _ in range(self.num_players)]

    def seed(self, seed: int) -> None:
        """
        Sets a seed.
        """
        
        self.game.np_random = np.random.RandomState(seed)

    def _get_legal_actions(self):
        """
        Gets the legal actions from judger.
        """
        
        legal_actions = self.game.judger.get_legal_actions()
        return {action.action_id: True for action in legal_actions}

    def _extract_state(self, state):
        """
        Extracts state representation from the game state as a dictionary.
        """
        
        raw_info = state['raw_state_info']
        obs = {}
        
        # Layouts: (8, 2) tensor [open_card_id, hidden_card_id]
        my_layout_tensor = np.full((config.NUM_COLUMNS_PER_PLAYER, 2), 32, dtype=np.int32)
        for i, col in enumerate(raw_info['my_layout']):
            if col.open_card:
                my_layout_tensor[i, 0] = col.open_card.card_id
                
            # The hidden card IDs dependent on information level
            if col.closed_card and raw_info.get('my_hidden_cards'):
                my_layout_tensor[i, 1] = col.closed_card.card_id
        obs['my_layout_tensor'] = my_layout_tensor

        # Opponent layout
        opponent_layout_tensor = np.full((config.NUM_COLUMNS_PER_PLAYER, 2), 32, dtype=np.int32)
        for i, col in enumerate(raw_info['opponent_layout']):
            if col.open_card:
                opponent_layout_tensor[i, 0] = col.open_card.card_id
                
            # The hidden card IDs dependent on information level
            if col.closed_card and raw_info.get('opponent_hidden_cards'):
                opponent_layout_tensor[i, 1] = col.closed_card.card_id
        obs['opponent_layout_tensor'] = opponent_layout_tensor
        
        # Unaccounted card mask: 32 vector
        known_card_ids = set(card.card_id for card in raw_info['played_cards'])
        known_card_ids.update(card.card_id for _, card in raw_info['trick_moves'])

        known_card_ids.update(my_layout_tensor[my_layout_tensor != 32])
        known_card_ids.update(opponent_layout_tensor[opponent_layout_tensor != 32])

        unaccounted_mask = np.ones(32, dtype=np.float32)
        for card_id in known_card_ids:
            if 0 <= card_id < 32:
                unaccounted_mask[card_id] = 0.0
        obs['unaccounted_cards_mask'] = unaccounted_mask

        # Current trick and cementery card IDs: lists
        obs['trick_card_ids'] = [card.card_id for _, card in raw_info['trick_moves']]
        obs['cemetery_card_ids'] = [card.card_id for card in raw_info['played_cards']]

        # Hidden Card Indicators: 8 vector
        my_hidden = np.zeros(config.NUM_COLUMNS_PER_PLAYER, dtype=np.float32)
        for i, col in enumerate(raw_info['my_layout']):
            if col.has_card_underneath():
                my_hidden[i] = 1.0
        obs['my_hidden_indicators'] = my_hidden

        opponent_hidden = np.zeros(config.NUM_COLUMNS_PER_PLAYER, dtype=np.float32)
        for i, col in enumerate(raw_info['opponent_layout']):
            if col.has_card_underneath():
                opponent_hidden[i] = 1.0
        obs['opponent_hidden_indicators'] = opponent_hidden
        
        # Normalized Context Feature Vector (11,)
        MAX_SCORE = 480.0
        MAX_TRICKS = 16.0
        
        context = np.zeros(11, dtype=np.float32)
        
        if raw_info['trump_suit'] is not None:
            trump_idx = DeclareTrumpAction.VALID_TRUMPS.index(raw_info['trump_suit'])
            context[trump_idx] = 1.0
        
        context[5] = 1.0 if raw_info['round_phase'] == 'play' else 0.0
        context[6] = float(raw_info['current_player_id'])
        context[7] = float(raw_info['trick_leader_id'])
        context[8] = np.clip(float(raw_info['my_score']) / MAX_SCORE, 0.0, 1.0)
        context[9] = np.clip(float(raw_info['opponent_score']) / MAX_SCORE, 0.0, 1.0)
        context[10] = float(raw_info['tricks_played']) / MAX_TRICKS

        obs['context'] = context

        # Padded Action History Tensor
        history_tensor = np.zeros((config.HISTORY_SEQUENCE_LENGTH, config.HISTORY_FRAME_SIZE), dtype=np.float32)
        history_frames = raw_info['history_frames']
        if history_frames:
            num_frames = len(history_frames)
            if num_frames > 0:
                history_matrix = np.vstack(history_frames)
                
                # Pad at the beginning of the tensor
                history_tensor[-num_frames:] = history_matrix
        
        obs['action_history'] = history_tensor

        return {
            'obs': obs,
            'legal_actions': self._get_legal_actions(),
            'raw_state_info': raw_info,
            'raw_legal_actions': list(self._get_legal_actions().keys()),
            'action_record': self.action_recorder,
        }

    def get_payoffs(self):
        """
        Gets the payoffs of the game.
        """
        
        return np.array(self.game.get_payoffs(), dtype=np.float32)

    def get_scores(self):
        """
        Gets the scores of the game.
        """
        
        return np.array([p.score for p in self.game.players], dtype=np.int32)

    def _decode_action(self, action_id):
        """
        Decodes an action ID into ActionEvent.
        """
        
        return ActionEvent.from_action_id(action_id)

    def get_perfect_information(self):
        """
        Gets the perfect information of the game.
        """
        
        p0 = self.game.players[0]
        p1 = self.game.players[1]
        
        return {
            'player_0_layout_open': [c.card_id for c in p0.get_playable_cards()],
            'player_0_layout_hidden': [c.card_id for c in p0.get_hidden_cards()],
            'player_1_layout_open': [c.card_id for c in p1.get_playable_cards()],
            'player_1_layout_hidden': [c.card_id for c in p1.get_hidden_cards()],
            'trump_suit': self.game.round.trump_suit if self.game.round else None,
            'current_phase': self.game.round.round_phase if self.game.round else None,
            'trick_moves': [c.card_id for _, c in (self.game.round.trick_moves if self.game.round else [])]
        }
    
    def clone(self):
        """
        Creates a copy of the environment object.
        """
        
        cloned_env = BauernskatEnv(copy.copy(self.config))
        cloned_env.game = self.game.clone()
        return cloned_env