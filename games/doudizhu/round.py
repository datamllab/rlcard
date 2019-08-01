# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import functools
from core import Round
from dealer import DoudizhuDealer
from methods import cards2str


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
        self.dealer = DoudizhuDealer()
        while True:
            landlord_num = self.dealer.determine_role(players)
            if landlord_num is not None:
                break
        print('\n###############')
        for player in players:
            player.print_remained_card()
        print('###############')
        seen_cards = self.dealer.deck[-3:]
        seen_cards.sort(key=functools.cmp_to_key(DoudizhuDealer.doudizhu_sort))
        self.seen_cards = cards2str(seen_cards)
        print('seen cards:', self.seen_cards)
        print('以上为初始化Game时，随机进行的一个选地主过程\n')
        self.landlord_num = landlord_num

    def proceed_round(self, player, action):
        """
        Call other Classes's functions to keep one round running
        """
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
