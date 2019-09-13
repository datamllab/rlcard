
import random
from rlcard.core import Dealer
from rlcard.utils.utils import init_standard_deck

class LimitholdemDealer(Dealer):

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
        ''' Distribute one card to the player
        Args:
            player_id (int): the target player's id
        '''

        return self.deck.pop()

