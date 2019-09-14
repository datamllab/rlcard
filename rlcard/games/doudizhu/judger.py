# -*- coding: utf-8 -*-
''' Implement Doudizhu Judger class
'''

from rlcard.games.doudizhu.utils import CARD_TYPE
from rlcard.games.doudizhu.utils import cards2str, contains_cards


class DoudizhuJudger(object):
    ''' Determine what cards a player can play
    '''

    def __init__(self, players):
        ''' Initilize the Judger class for Dou Dizhu
        '''

        self.playable_cards = [CARD_TYPE.copy() for i in range(3)]
        for player in players:
            self.get_playable_cards(player)

    def get_playable_cards(self, player):
        ''' Provide all legal cards the player can play according to his
        current hand.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer

        Returns:
            list: list of string of playable cards
        '''

        player_id = player.player_id
        current_hand = cards2str(player.current_hand)
        missed = None
        for single in player.singles:
            if single not in current_hand:
                missed = single
                break
        playable_cards = list(self.playable_cards[player_id])
        if missed is not None:
            position = player.singles.find(missed)
            player.singles = player.singles[position+1:]
            for cards in playable_cards:
                if missed in cards or (not contains_cards(current_hand, cards)):
                    del self.playable_cards[player_id][cards]
        else:
            for cards in playable_cards:
                if not contains_cards(current_hand, cards):
                    del self.playable_cards[player_id][cards]
        return list(self.playable_cards[player_id])
