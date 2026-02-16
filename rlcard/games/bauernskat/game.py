'''
    File name: rlcard/games/bauernskat/game.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

import copy
from typing import List, Dict, Any
import numpy as np

from . import config
from .player import BauernskatPlayer
from .dealer import BauernskatDealer
from .round import BauernskatRound
from .judger import BauernskatJudger
from .action_event import ActionEvent, DeclareTrumpAction, PlayCardAction
from .card import BauernskatCard


class BauernskatGame:
    """
    BauernskatGame runs the game loop and provides information.
    """

    def __init__(self, allow_step_back: bool = False, information_level: str = 'normal') -> None:
        """
        Initializes BauernskatGame.
        """
        
        self.allow_step_back = allow_step_back
        self.information_level = information_level
        self.np_random: np.random.RandomState = np.random.RandomState()
        
        self.players: List[BauernskatPlayer] = []
        self.round: BauernskatRound = None
        self.judger: BauernskatJudger = BauernskatJudger(game=self)

    def get_num_players(self) -> int:
        """
        Returns the number of players.
        """
        
        return config.NUM_PLAYERS

    @staticmethod
    def get_num_actions() -> int:
        """
        Returns the total number of unique actions in the game.
        """
        
        return ActionEvent.get_num_actions()

    def init_game(self) -> tuple[Dict[str, Any], int]:
        """
        Initializes a new game of Bauernskat.
        """
        
        self.players = [BauernskatPlayer(i, self.np_random) for i in range(config.NUM_PLAYERS)]
        dealer = BauernskatDealer(self.np_random)

        dealer.deal_phase_one(self.players)

        self.round = BauernskatRound(dealer, self.players, self.np_random)

        current_player_id = self.get_player_id()
        state = self.get_state(current_player_id)

        return state, current_player_id

    def step(self, action: ActionEvent) -> tuple[Dict[str, Any], int]:
        """
        Executes an action and transitions to the next state.
        """
        
        if isinstance(action, int):
            decoded_action = ActionEvent.from_action_id(action)
        else:
            decoded_action = action
        
        if self.is_over():
            raise ValueError("Cannot perform an action in a completed game.")

        if isinstance(decoded_action, DeclareTrumpAction):
            self.round.declare_trump(decoded_action)
        elif isinstance(decoded_action, PlayCardAction):
            self.round.play_card(decoded_action)

        next_player_id = self.get_player_id()
        next_state = self.get_state(next_player_id)
        
        return next_state, next_player_id

    def get_state(self, player_id: int) -> Dict[str, Any]:
        """
        Generates a state representation for a specific player.
        """
        
        player = self.players[player_id]
        opponent = self.players[1 - player_id]

        legal_actions = self.judger.get_legal_actions()
        legal_actions_dict = {action.action_id: True for action in legal_actions}
        
        # Contains all dynamic informations about the game state.
        raw_state_info = {
            'round_phase': self.round.round_phase if self.round else 'declare_trump',
            'my_cards': player.get_playable_cards(),
            'opponent_visible_cards': opponent.get_playable_cards(),
            'my_layout': player.layout,
            'opponent_layout': opponent.layout,
            'trick_moves': self.round.trick_moves if self.round else [],
            'trump_suit': self.round.trump_suit if self.round else None,
            'current_player_id': self.get_player_id(),
            'trick_leader_id': self.round.trick_leader_id if self.round else 0,
            'tricks_played': self.round.tricks_played if self.round else 0,
            'player_id': player_id,
            'my_score': player.score,
            'opponent_score': opponent.score,
            'played_cards': self.round.played_cards if self.round else set(),
            'history_frames': self.round.history_frames if self.round else [],
        }

        # Constraints asymmetric information level for a player.
        if isinstance(self.information_level, dict):
            current_level = self.information_level.get(player_id, 'normal')
        else:
            current_level = self.information_level

        # Optionally add hidden card informations based on the information level.
        if current_level in ('show_self', 'perfect'):
            raw_state_info['my_hidden_cards'] = player.get_hidden_cards()
        else:
            raw_state_info['my_hidden_cards'] = []

        if current_level == 'perfect':
            raw_state_info['opponent_hidden_cards'] = opponent.get_hidden_cards()
        else:
            raw_state_info['opponent_hidden_cards'] = []

        state = {
            'legal_actions': legal_actions_dict,
            'raw_state_info': raw_state_info
        }
        
        if self.is_over():
            p0_score = self.players[0].score
            p1_score = 120 - p0_score
            
            if player_id == 0:
                state['raw_state_info']['pip_difference'] = p0_score - p1_score
            else:
                state['raw_state_info']['pip_difference'] = p1_score - p0_score
            
            game_payoffs = self.get_payoffs()
            state['raw_state_info']['game_value_payoff'] = game_payoffs[player_id]
            
        return state

    def get_payoffs(self) -> List[float]:
        """
        Determines the payoffs at the end of the game based on actual Skat scoring.
        """
        
        if not self.is_over():
            return [0.0, 0.0]

        # Winner based on pips
        p0_score = self.players[0].score
        
        assert 0 <= p0_score <= 120, f"Invalid score for Player 0: {p0_score}"
        
        p1_score = 120 - p0_score
        
        # A tie means the Geber wins
        declarer_wins = p0_score >= 61

        # Base game value
        base_values = {'C': 12, 'S': 11, 'H': 10, 'D': 9, 'G': 24}
        trump_suit = self.round.trump_suit
        base_value = base_values.get( trump_suit, 0)

        # Matador count
        shuffled_deck = self.round.dealer.shuffled_deck
        p0_card_indices = [
            31, 30, 29, 28, 23, 22, 21, 20, 15, 14, 13, 12, 7, 6, 5, 4
        ]
        p0_initial_hand = {shuffled_deck[i] for i in p0_card_indices}

        jacks_in_order = [
            BauernskatCard('C', 'J'), BauernskatCard('S', 'J'),
            BauernskatCard('H', 'J'), BauernskatCard('D', 'J')
        ]
        
        matador_count = 0
        has_club_jack = jacks_in_order[0] in p0_initial_hand
        
        if has_club_jack:
            # With n matadors
            for jack in jacks_in_order:
                if jack in p0_initial_hand: matador_count += 1
                else: break
        else:
            # Without n matadors
            for jack in jacks_in_order:
                if jack not in p0_initial_hand: matador_count += 1
                else: break
        
        # Base multiplier
        base_multiplier = matador_count + 1
        game_value = base_value * base_multiplier

        # Calculate payoffs
        if declarer_wins:
            final_score = game_value
            # Apply Schneider or Schwarz multipliers
            if p1_score == 0:
                final_score *= 4
            elif p1_score < 31:
                final_score *= 2
        else:
            # The Vorhand loses twice the game value
            final_score = -2 * game_value
            
        return [float(final_score), float(-final_score)]

    def get_player_id(self) -> int:
        """
        Returns the ID of the player of the current turn.
        """
        
        if self.round is None:
            return 0
        
        return self.round.current_player_id

    def is_over(self) -> bool:
        """
        Checks if the game has ended.
        """
        
        if self.round is None:
            return False
        
        return self.round.is_over()
    
    def clone(self):
        """
        Creates a deep copy of the game object for simulations.
        """
        
        cloned_game = BauernskatGame(allow_step_back=self.allow_step_back, information_level=self.information_level)
        cloned_game.np_random.set_state(self.np_random.get_state())

        if self.round:
            cloned_game.round = copy.deepcopy(self.round)
            cloned_game.players = cloned_game.round.players
        else:
            cloned_game.players = copy.deepcopy(self.players)
            cloned_game.round = None
        
        cloned_game.judger = BauernskatJudger(game=cloned_game)
        
        return cloned_game