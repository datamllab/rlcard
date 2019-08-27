# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import functools
from rlcard.core import Round
from rlcard.games.doudizhu.dealer import DoudizhuDealer as Dealer
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger

class DoudizhuRound(Round):
    """
    Round can call other Classes' functions to keep the game running
    """

    def __init__(self, players):
        """Determine the landlord

        Args:
            players: a list of Player objects

        Notes:
            greater_player: the winner in one round
            dealer: a instance of DouzizhuDealer
            cards_seen: cards given to landlord after determining landlord
            landlord_num: the id of landlord
        """
        self.greater_player = None
        self.dealer = Dealer()
        landlord_num = self.dealer.determine_role_ii(players)
        #while True:
        #    landlord_num = self.dealer.determine_role(players)
        #    if landlord_num is not None:
        #        break
        # print('\n############### Doudizhu Initiate ###############')
        # for player in players:
            # player.print_remaining_card()
        cards_seen = self.dealer.deck[-3:]
        cards_seen.sort(key=functools.cmp_to_key(Dealer.doudizhu_sort))
        self.cards_seen = Judger.cards2str(cards_seen)
        # print('seen cards:', self.cards_seen)
        # print('#################################################\n')
        self.landlord_num = landlord_num

    def proceed_round(self, player, action):
        """
        Call other Classes's functions to keep one round running
        """
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
