'''
    File name: bridge/player.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from .utils.bridge_card import BridgeCard


class BridgePlayer:

    def __init__(self, player_id: int, np_random):
        ''' Initialize a BridgePlayer player class

        Args:
            player_id (int): id for the player
        '''
        if player_id < 0 or player_id > 3:
            raise Exception(f'BridgePlayer has invalid player_id: {player_id}')
        self.np_random = np_random
        self.player_id: int = player_id
        self.hand: List[BridgeCard] = []

    def remove_card_from_hand(self, card: BridgeCard):
        self.hand.remove(card)

    def __str__(self):
        return ['N', 'E', 'S', 'W'][self.player_id]
