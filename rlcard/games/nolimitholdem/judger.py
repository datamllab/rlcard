from rlcard.games.limitholdem.judger import LimitholdemJudger
from rlcard.games.limitholdem.utils import *

class NolimitholdemJudger(LimitholdemJudger):
    ''' The Judger class for Texas Hold'em
    '''

    def __init__(self):
        ''' Initialize a judger class
        '''

        super(NolimitholdemJudger, self).__init__()