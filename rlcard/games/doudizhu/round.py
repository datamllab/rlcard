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
            seen_cards: cards given to landlord after determining landlord
            landlord_num: the id of landlord
        """
        self.greater_player = None
        self.dealer = Dealer()
        while True:
            landlord_num = self.dealer.determine_role(players)
            if landlord_num is not None:
                break
        # print('\n############### Doudizhu Initiate ###############')
        # for player in players:
            # player.print_remained_card()
        seen_cards = self.dealer.deck[-3:]
        seen_cards.sort(key=functools.cmp_to_key(Dealer.doudizhu_sort))
        self.seen_cards = Judger.cards2str(seen_cards)
        # print('seen cards:', self.seen_cards)
        # print('#################################################\n')
        self.landlord_num = landlord_num

    def proceed_round(self, player, action):
        """
        Call other Classes's functions to keep one round running
        """
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
