'''
    File name: rlcard/games/bauernskat/dealer.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

from typing import List
import numpy as np

from .player import BauernskatPlayer
from .card import BauernskatCard
from . import config


class BauernskatDealer:
    """
    The BauernskatDealer shuffles the deck and deals cards in the two phases.
    """

    def __init__(self, np_random: np.random.RandomState) -> None:
        """
        Initializes BauernskatDealer.
        """
        
        self.np_random: np.random.RandomState = np_random
        
        self.shuffled_deck: List[BauernskatCard] = BauernskatCard.get_deck()
        self.np_random.shuffle(self.shuffled_deck)

        self._card_stack: List[BauernskatCard] = self.shuffled_deck.copy()

    def deal_phase_one(self, players: List[BauernskatPlayer]) -> None:
        """
        Deals the first 12 cards to set up for trump declaration.
        - Deals 4 closed cards to Vorhand.
        - Deals 4 closed cards to Geber.
        - Deals 4 open cards to Vorhand.
        Then the dealer will pause for the Vorhand to declare trump before continuing.
        """
        
        assert len(players) == config.NUM_PLAYERS, "Dealing requires exactly two players."
        
        vorhand, geber = players[0], players[1]
        num_cols_half = config.NUM_COLUMNS_PER_PLAYER // 2

        # Deal 4 closed cards to Vorhand
        for i in range(0, num_cols_half):
            vorhand.layout[i].closed_card = self._card_stack.pop()

        # Deal 4 closed cards to Geber
        for i in range(0, num_cols_half):
            geber.layout[i].closed_card = self._card_stack.pop()

        # Deal 4 open cards to Vorhand
        for i in range(0, num_cols_half):
            vorhand.layout[i].open_card = self._card_stack.pop()
            
    def deal_phase_two(self, players: List[BauernskatPlayer]) -> None:
        """
        Deal the remaining 20 cards after the trump has been declared.
        """
        assert len(players) == config.NUM_PLAYERS, "Dealing requires exactly two players."

        vorhand, geber = players[0], players[1]
        num_cols_half = config.NUM_COLUMNS_PER_PLAYER // 2
        
        # Deal 4 open cards to Geber
        for i in range(0, num_cols_half):
            geber.layout[i].open_card = self._card_stack.pop()

        # Deal 4 closed cards to Vorhand
        for i in range(num_cols_half, config.NUM_COLUMNS_PER_PLAYER):
            vorhand.layout[i].closed_card = self._card_stack.pop()

        # Deal 4 closed cards to Geber
        for i in range(num_cols_half, config.NUM_COLUMNS_PER_PLAYER):
            geber.layout[i].closed_card = self._card_stack.pop()

        # Deal 4 open to Vorhand
        for i in range(num_cols_half, config.NUM_COLUMNS_PER_PLAYER):
            vorhand.layout[i].open_card = self._card_stack.pop()

        # Deal 4 open cards to Geber
        for i in range(num_cols_half, config.NUM_COLUMNS_PER_PLAYER):
            geber.layout[i].open_card = self._card_stack.pop()

        assert len(self._card_stack) == 0, "All cards should have been dealt."