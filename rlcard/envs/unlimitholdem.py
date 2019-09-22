from rlcard.envs.limitholdem import LimitholdemEnv

from rlcard.games.unlimitholdem.game import UnlimitholdemGame as Game
from rlcard.utils.utils import *

class UnlimitholdemEnv(LimitholdemEnv):
    ''' Limitholdem Environment
    '''

    def __init__(self):
        ''' Initialize the Limitholdem environment
        '''

        super(UnlimitholdemEnv, self).__init__()
