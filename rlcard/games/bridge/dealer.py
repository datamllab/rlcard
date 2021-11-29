'''
    File name: bridge/dealer.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from .player import BridgePlayer
from .utils.bridge_card import BridgeCard


class BridgeDealer:
    ''' Initialize a BridgeDealer dealer class
    '''
    def __init__(self, np_random):
        ''' set shuffled_deck, set stock_pile
        '''
        self.np_random = np_random
        self.shuffled_deck: List[BridgeCard] = BridgeCard.get_deck()  # keep a copy of the shuffled cards at start of new hand
        self.np_random.shuffle(self.shuffled_deck)
        self.stock_pile: List[BridgeCard] = self.shuffled_deck.copy()

    def deal_cards(self, player: BridgePlayer, num: int):
        ''' Deal some cards from stock_pile to one player

        Args:
            player (BridgePlayer): The BridgePlayer object
            num (int): The number of cards to be dealt
        '''
        for _ in range(num):
            player.hand.append(self.stock_pile.pop())
