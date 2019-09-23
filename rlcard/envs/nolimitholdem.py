from rlcard.envs.limitholdem import LimitholdemEnv

from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game
from rlcard.utils.utils import *

class NolimitholdemEnv(LimitholdemEnv):
    ''' Nolimitholdem Environment
    '''

    def __init__(self):
        ''' Initialize the Nolimitholdem environment
        '''

        super(NolimitholdemEnv, self).__init__()
    
    ''' TODO: nolimitholdem
    '''