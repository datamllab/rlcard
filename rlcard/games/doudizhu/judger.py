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

    @staticmethod
    def judge_game(players, player_id):
        ''' Judge whether the game is over

        Args:
            players (list): list of DoudizhuPlayer objects
            player_id (int): integer of player's id

        Returns:
            (bool): True if the game is over
        '''
        player = players[player_id]
        if not player.current_hand:
            return True
        return False

    @staticmethod
    def judge_payoffs(landlord_id, winner_id):
        payoffs = [0, 0, 0]
        if winner_id == landlord_id:
            payoffs[landlord_id] = 1
        else:
            for index, payoffs in enumerate(payoffs):
                if index != landlord_id:
                    payoffs[index] = 1
        return payoffs
