# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import sys
import functools
from os import path
from core import Round
from dealer import DoudizhuDealer
from methods import cards2str
from utils.utils import get_downstream_player_id, get_upstream_player_id


class DoudizhuRound(Round):
    """
    Round can call other Classes' functions to keep the game running
    """

    def __init__(self, players):
        """Determine the landlord

        Args:
            players: a list of Player objects

        Member Vars:
            greater_player: the winner in one round
            round_id: the id of the round
            dealer: a instance of DouzizhuDealer
            seen_cards: cards given to landlord after having determined landlord
        """
        self.greater_player = None
        self.round_id = 0
        self.round_last = None
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
        print('seen cards', self.seen_cards)
        print()
        #print('The id of the landlord is '+str(landlord_num))
        self.landlord_num = landlord_num

    def proceed_round(self, player, action):
        """
        Call other Classes's functions to keep one round running

        Args:
            players: a list of players
            start: The id of the first player to play in one round
                   (landlord or winner in last round)
        Return:
            tuple: (1(if game over)/0(if not),
                   the id of the winner in this round)
        """
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
