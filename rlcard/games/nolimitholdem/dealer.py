from rlcard.games.limitholdem import Dealer

class NolimitholdemDealer(Dealer):

    def __init__(self, np_random):
        ''' Initialize a nolimitholdem dealer class
        '''
        super(NolimitholdemDealer, self).__init__(np_random)
