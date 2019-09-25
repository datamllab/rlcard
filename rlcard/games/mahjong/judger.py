# -*- coding: utf-8 -*-
''' Implement Mahjong Judger class
'''



class MahjongJudger(object):
    ''' Determine what cards a player can play
    '''

    def __init__(self, players):
        ''' Initilize the Judger class for Dou Dizhu
        '''

        self.playable_cards = [CARD_TYPE.copy() for i in range(3)]
        for player in players:
            self.get_playable_cards(player)

    def judge_round(self):
