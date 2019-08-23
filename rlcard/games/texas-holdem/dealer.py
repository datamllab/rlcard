# -*- coding: utf-8 -*-
"""Implement Texasholdem Dealer class"""
import random
from rlcard.core import Dealer
from rlcard.utils.utils import init_standard_deck
from itertools import product
import random
import copy


class TexasDealer(Dealer):
    """Dealer can shuffle, deal cards, and determine players' postions
    """

    rank_list = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
                 'A']

    def __init__(self):
        """Give dealer the deck

        Notes:
            deck: standard cards
        """
        super().__init__()
        self.deck = init_standard_deck()

    def shuffle(self):
        random.shuffle(self.deck)

    @staticmethod
    def texas_sort(card_A, card_B):
        """Sort the cards from the smaller to the greater
        """
        key = []
        for card in [card_A, card_B]:
            if card.rank == '':
                key.append(TexasDealer.rank_list.index(card.suit))
            else:
                key.append(TexasDealer.rank_list.index(card.rank))
        if key[0] > key[1]:
            return 1
        if key[0] < key[1]:
            return -1
        return 0
    
    def deal_hands(self, players):
        """Deal two hidden hand cards to player

        Args:
            players: a list of Player objects
        """
        hand_num = 2
        for index, player in enumerate(players):
            player.hand = self.deck[index*hand_num:(index+1)*hand_num]
            player.remained_cards = copy.deepcopy(player.hand)

    def deal_cards(self, players):
        """Deal visible cards to player

        Args:
            players: a list of Player objects
        """
        hand_num = 1
        for index, player in enumerate(players):
            player.hand = player.hand.append(self.deck[index*hand_num:(index+1)*hand_num])
            player.remained_cards = copy.deepcopy(player.hand)