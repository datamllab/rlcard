import random

from rlcard.utils.utils import init_standard_deck
from rlcard.games.limitholdem.dealer import LimitholdemDealer

class UnlimitholdemDealer(LimitholdemDealer):

    def __init__(self):
        ''' Initialize a unlimitholdem dealer class
        '''

        super(UnlimitholdemDealer, self).__init__()
