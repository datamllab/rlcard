import utils as utils
import numpy as np


class BeloteDealer:

    def __init__(self, np_random):
        ''' Initialize a Belote-decouverte dealer class
        '''
        self.deck = utils.init_8_deck()
        self.np_random = np_random

        self.shuffle()

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_cards(self, player, num):
        self.deal_8(player)

    def deal_8(self, player):
        ''' Deal 8 cards (4 to each player) :
            2 in hand
            1 on the table (visible by everyone)
            1 secret
        '''
        player.hand.append(self.deck.pop())
        player.hand.append(self.deck.pop())
        player.secret.append(self.deck.pop())
        player.table.append(self.deck.pop())

    def deal_first_five(self, player):
        return NotImplementedError

    def deal_secret(self, player):
        return NotImplementedError

    def deal_table(self, player):
        return NotImplementedError


# # For test
# if __name__ == '__main__':
#    dealer = BeloteDealer(np.random.RandomState())
#    for card in dealer.deck:
#        print(card.__str__())
#    print(len(dealer.deck))
