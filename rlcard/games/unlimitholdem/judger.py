from rlcard.games.limitholdem.judger import LimitholdemJudger
from rlcard.games.limitholdem.utils import *

class UnlimitholdemJudger(LimitholdemJudger):
    ''' The Judger class for Texas Hold'em
    '''

    def __init__(self):
        ''' Initialize a judger class
        '''

        super(UnlimitholdemJudger, self).__init__()