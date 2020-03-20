'''
    File name: gin_rummy/dealer.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List

import random

from rlcard.games.gin_rummy.card import Card, get_deck
from rlcard.games.gin_rummy.player import GinRummyPlayer


class GinRummyDealer(object):
    ''' Initialize a GinRummy dealer class
    '''
    def __init__(self):
        ''' Empty discard_pile, set shuffled_deck, set stock_pile
        '''
        self.discard_pile = []  # type: List[Card]
        self.shuffled_deck = get_deck().copy()  # keep a copy of the shuffled cards at start of new hand
        random.shuffle(self.shuffled_deck)
        self.stock_pile = self.shuffled_deck.copy()  # type: List[Card]

    def deal_cards(self, player: GinRummyPlayer, num: int):
        ''' Deal some cards from stock_pile to one player

        Args:
            player (GinRummyPlayer): The GinRummyPlayer object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())
