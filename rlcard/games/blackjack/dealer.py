import random

from rlcard.utils.utils import init_standard_deck


class BlackjackDealer(object):

    def __init__(self):
        ''' Initialize a Blackjack dealer class
        '''
        super().__init__()
        self.deck = init_standard_deck()
        self.shuffle()
        self.hand = []
        self.status = 'alive'
        self.score = 0

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
