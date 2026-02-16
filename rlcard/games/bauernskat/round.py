'''
    File name: rlcard/games/bauernskat/round.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

from typing import List, Optional, Tuple
import numpy as np

from . import config
from .player import BauernskatPlayer
from .dealer import BauernskatDealer
from .card import BauernskatCard
from .action_event import ActionEvent, DeclareTrumpAction, PlayCardAction


class BauernskatRound:
    """
    Manages the state and progression of a single round in Bauernskat.
    """

    def __init__(self, dealer: BauernskatDealer, players: List[BauernskatPlayer], np_random: np.random.RandomState) -> None:
        """
        Initializes BauernskatRound.
        """
        
        self.np_random: np.random.RandomState = np_random
        self.dealer: BauernskatDealer = dealer
        self.players: List[BauernskatPlayer] = players
        
        self.round_phase: str = 'declare_trump'
        self.current_player_id: int = 0
        self.trick_leader_id: int = 0
        self.trump_suit: Optional[str] = None
        
        self.trick_moves: List[Tuple[int, BauernskatCard]] = []
        self.tricks_played: int = 0
        self.played_cards: set[BauernskatCard] = set()

        self.history_frames: List[np.ndarray] = []

    def _create_history_frame(self, action: ActionEvent) -> np.ndarray:
        """
        Creates a history frame vector based on the current game state and taken action.
        """
        acting_player_id = self.current_player_id
        
        # Encode Player
        player_vec = np.zeros(2, dtype=np.float32)
        player_vec[acting_player_id] = 1
        
        # Encode Action
        action_vec = np.zeros(37, dtype=np.float32)
        if isinstance(action, DeclareTrumpAction):
            trump_idx = DeclareTrumpAction.VALID_TRUMPS.index(action.trump_suit)
            action_vec[32 + trump_idx] = 1
        elif isinstance(action, PlayCardAction):
            suit_idx = BauernskatCard.suits.index(action.card.suit)
            rank_idx = BauernskatCard.ranks.index(action.card.rank)
            action_vec[suit_idx * 8 + rank_idx] = 1
            
        # Encode Context
        # Normalized pip scores
        my_score = self.players[acting_player_id].score
        opp_score = self.players[1 - acting_player_id].score
        
        # Trump suit
        trump_vec = np.zeros(5, dtype=np.float32)
        if self.trump_suit is not None:
            trump_idx = DeclareTrumpAction.VALID_TRUMPS.index(self.trump_suit)
            trump_vec[trump_idx] = 1
            
        # Trick Leader
        leader_vec = np.zeros(2, dtype=np.float32)
        leader_vec[self.trick_leader_id] = 1
        
        # Normalized count of tricks played
        tricks_played_count = self.tricks_played

        context_vec = np.concatenate([
            [my_score / 120.0, opp_score / 120.0],
            trump_vec,
            leader_vec,
            [tricks_played_count / 16.0]
        ])

        # Concatenated frame vector
        final_frame = np.concatenate([player_vec, action_vec, context_vec])
        
        assert final_frame.shape[0] == config.HISTORY_FRAME_SIZE
        
        return final_frame

    def declare_trump(self, action: DeclareTrumpAction) -> None:
        """
        Processes a DeclareTrumpAction and records it in the history.
        """
        
        assert self.round_phase == 'declare_trump', "Trump can only be declared once."
        assert self.current_player_id == 0, "Only Vorhand can declare trump."

        frame = self._create_history_frame(action)
        self.history_frames.append(frame)

        self.trump_suit = action.trump_suit
        self.dealer.deal_phase_two(self.players)
        self.round_phase = 'play'
        self.trick_leader_id = 0
        self.current_player_id = 0
    
    def play_card(self, action: PlayCardAction) -> None:
        """
        Processes a PlayCardAction and records it in the history.
        """
        
        assert self.round_phase == 'play', "Cannot play a card outside of the 'play' phase."
        
        card_to_play = action.card
        player = self.players[self.current_player_id]
        
        column = player.find_column_for_card(card_to_play)
        assert column is not None, f"{player} tried to play {card_to_play}, which is not in their layout."
        
        frame = self._create_history_frame(action)
        self.history_frames.append(frame)
        
        column.play_card()
        self.trick_moves.append((self.current_player_id, card_to_play))
        
        if len(self.trick_moves) == 1:
            self.current_player_id = 1 - self.current_player_id
        else:
            self._process_trick()
    
    def _get_card_strength(self, card: BauernskatCard, led_suit: str) -> int:
        """
        Determines the strength of a card based on the current trump and started suit.
        """
        
        STRENGTH_MAP = {'7': 0, '8': 1, '9': 2, 'Q': 3, 'K': 4, '10': 5, 'A': 6, 'J': 7}
        if self.trump_suit != 'G':
            if card.rank == 'J':
                jack_strength = {'C': 3, 'S': 2, 'H': 1, 'D': 0}
                return 400 + jack_strength[card.suit]
            if card.suit == self.trump_suit:
                return 300 + STRENGTH_MAP[card.rank]
        if card.suit == led_suit:
            STRENGTH_MAP_SUIT = {'7': 0, '8': 1, '9': 2, 'J': 3, 'Q': 4, 'K': 5, '10': 6, 'A': 7}
            return 200 + STRENGTH_MAP_SUIT[card.rank]
        return 100 + STRENGTH_MAP[card.rank]

    def _determine_trick_winner(self) -> int:
        """
        Determines the trick winner.
        """
        
        assert len(self.trick_moves) == 2, "A trick must have exactly two cards to determine a winner."
        
        leader_id, leader_card = self.trick_moves[0]
        follower_id, follower_card = self.trick_moves[1]
        led_suit = leader_card.suit
        leader_strength = self._get_card_strength(leader_card, led_suit)
        follower_strength = self._get_card_strength(follower_card, led_suit)
        
        return leader_id if leader_strength > follower_strength else follower_id
        
    def _process_trick(self) -> None:
        """
        Awards pips and updates state.
        """
        
        winner_id = self._determine_trick_winner()
        trick_points = self.trick_moves[0][1].points + self.trick_moves[1][1].points
        self.players[winner_id].add_points(trick_points)
        self.played_cards.add(self.trick_moves[0][1])
        self.played_cards.add(self.trick_moves[1][1])
        self.trick_moves = []
        self.tricks_played += 1
        self.trick_leader_id = winner_id
        self.current_player_id = winner_id
        if self.is_over():
            self.round_phase = 'game_over'

    def is_over(self) -> bool:
        """
        Checks if the round is over.
        """
        
        total_tricks = config.NUM_COLUMNS_PER_PLAYER * 2
        return self.tricks_played == total_tricks