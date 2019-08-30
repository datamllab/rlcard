
import random
from rlcard.core import Dealer
from rlcard.utils.utils import init_standard_deck

class BlackjackDealer(Dealer):

    def __init__(self):

        super().__init__()
        self.deck = init_standard_deck()
        self.shuffle()
        self.hand = []
        self.status = 'alive'
        self.score = 0

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_card(self, player):
        self.deal_one_card_to(player)
    
    def deal_one_card_to(self, player):
        card = self.deck.pop()
        player.hand.append(card)
