from rlcard.games.limitholdem import Judger


class NolimitholdemJudger(Judger):
    """The Judger class for not limit texas holdem"""
    def __init__(self, np_random):
        """ Initialize a judger class"""
        super(NolimitholdemJudger, self).__init__(np_random)
