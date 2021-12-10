from rlcard.utils import init_standard_deck
import numpy as np

class DurakDealer:

    def __init__(self, np_random):
        ''' Initialize a Durak dealer class
        '''
        self.np_random = np_random
        self.deck = init_standard_deck()
        self.shuffle()
        self.set_super_suite()

    def shuffle(self):
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player):
        ''' Deal missing cards from deck to one player

        Args:
            player (object): The object of DoudizhuPlayer
        '''
        for _ in range(player.missing_cards):
            if not self.empty():
                player.hand.append(self.deck.pop())

    def set_super_suite(self):
        ''' Set last card of  the deck as super suite

        Args:
            player (object): The object of DoudizhuPlayer
        '''
        self.super_suite = self.deck[0]

    def empty(self):
        return len(self.deck) == 0