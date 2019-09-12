
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

    def deal_card(self, player):
        ''' Distribute one card to the player
        Args:
            player_id (int): the target player's id
        '''
        card = self.deck.pop()
        player.hand.append(card)

    def deal_chips(self, player, chips_num):
        ''' For call & raise action
        Args:
            player: the player who take the action
            chips_num: the value of chips in the action
        '''
        chips_num = chips_num
        self.pot = self.pot + chips_num
        player.chips_remaining = player.chips_remaining - chips_num



