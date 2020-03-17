'''
    File name: gin_rummy/player.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.card import Card

from typing import List


class GinRummyPlayer(object):

    def __init__(self, player_id: int):
        ''' Initialize a GinRummy player class

        Args:
            player_id (int): id for the player
        '''
        self.player_id = player_id
        self.hand = []
        self.known_cards = []  # opponent knows cards picked up by player and not yet discarded

    def get_player_id(self) -> int:
        ''' Return player's id
        '''
        return self.player_id

    def __str__(self):
        return "N" if self.player_id == 0 else "S"

    @classmethod
    def opponent_of(cls, player: 'GinRummyPlayer') -> 'GinRummyPlayer':
        return GinRummyPlayer(player_id=(player.player_id + 1) % 2)
