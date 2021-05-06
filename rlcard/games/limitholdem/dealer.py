from rlcard.utils.utils import init_standard_deck

class LimitholdemDealer:

    def __init__(self, np_random):
        ''' Initialize a limitholdem dealer class
        '''
        self.np_random = np_random
        self.deck = init_standard_deck()
        self.shuffle()
        self.pot = 0

    def shuffle(self):
        ''' Shuffle the deck
        '''
        self.np_random.shuffle(self.deck)

    def deal_card(self):
        ''' Deal one card from the deck

        Returns:
            (Card): The drawn card from the deck
        '''
        return self.deck.pop()
