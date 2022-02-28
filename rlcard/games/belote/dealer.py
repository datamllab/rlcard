from rlcard.utils import init_32_deck


class BeloteDealer:

    def __init__(self, np_random):
        ''' Initialize a Belote-decouverte dealer class
        '''
        self.deck = init_32_deck()
        self.np_random = np_random

        self.shuffle()


    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_card(self,player):
        return NotImplementedError

    def deal_first_five(self, player):
        return NotImplementedError

    def deal_secret(self, player):
        return NotImplementedError

    def deal_table(self, player):
        return NotImplementedError