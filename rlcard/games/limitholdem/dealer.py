import random

from rlcard.utils.utils import init_standard_deck

class LimitholdemDealer(object):

    def __init__(self):
        ''' Initialize a limitholdem dealer class
        '''

        super().__init__()
        self.deck = init_standard_deck()
        self.shuffle()
        self.pot = 0

    def shuffle(self):
        ''' Shuffle the deck
        '''

        random.shuffle(self.deck)

    def deal_card(self):
        ''' Deal one card from the deck

        Returns:
            (Card): The drawn card from the deck
        '''

        return self.deck.pop()
