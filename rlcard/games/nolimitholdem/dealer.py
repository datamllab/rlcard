from rlcard.games.limitholdem import Dealer


class NolimitholdemDealer(Dealer):
    def __init__(self, np_random):
        """Initialize a no limit holdem dealer class"""
        super(NolimitholdemDealer, self).__init__(np_random)
