from rlcard.core import Card
from rlcard.games.limitholdem.dealer import LimitholdemDealer

class LeducholdemDealer(LimitholdemDealer):

    def __init__(self):
        ''' Initialize a leducholdem dealer class
        '''

        self.deck = [Card('S', 'J'), Card('S', 'J'), Card('S', 'Q'), Card('S', 'Q'), Card('S', 'K'), Card('S', 'K')]
        self.shuffle()
        self.pot = 0
