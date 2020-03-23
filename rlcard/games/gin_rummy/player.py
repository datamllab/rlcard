'''
    File name: gin_rummy/player.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List

from rlcard.core import Card


class GinRummyPlayer(object):

    def __init__(self, player_id: int):
        ''' Initialize a GinRummy player class

        Args:
            player_id (int): id for the player
        '''
        self.player_id = player_id
        self.hand = []  # type: List[Card]
        self.known_cards = []  # type: List[Card]  # opponent knows cards picked up by player and not yet discarded

    def get_player_id(self) -> int:
        ''' Return player's id
        '''
        return self.player_id

    def __str__(self):
        return "N" if self.player_id == 0 else "S"

    @staticmethod
    def short_name_of(player_id: int) -> str:
        return "N" if player_id == 0 else "S"

    @staticmethod
    def opponent_id_of(player_id: int) -> int:
        return (player_id + 1) % 2
