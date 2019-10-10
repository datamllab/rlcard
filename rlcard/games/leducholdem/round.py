# -*- coding: utf-8 -*-
''' Implement Leduc Hold'em Round class
'''

from rlcard.games.limitholdem.round import LimitholdemRound

class LeducholdemRound(LimitholdemRound):
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self, raise_amount, allowed_raise_num, num_players):
        ''' Initilize the round class

        Args:
            raise_amount (int): the raise amount for each raise
            allowed_raise_num (int): The number of allowed raise num
            num_players (int): The number of players
        '''
        super(LeducholdemRound, self).__init__(raise_amount, allowed_raise_num, num_players)
