from rlcard.games.limitholdem.dealer import LimitholdemDealer

class NolimitholdemDealer(LimitholdemDealer):

    def __init__(self):
        ''' Initialize a nolimitholdem dealer class
        '''
        super(NolimitholdemDealer, self).__init__()
