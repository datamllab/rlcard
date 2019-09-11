# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import functools
from rlcard.core import Round
from rlcard.games.doudizhu.dealer import DoudizhuDealer as Dealer
from rlcard.games.doudizhu.judger import cards2str
from rlcard.games.doudizhu.utils import doudizhu_sort_card


class DoudizhuRound(Round):
    '''
    Round can call other Classes' functions to keep the game running
    '''

    def __init__(self):
        self.greater_player = None
        self.dealer = Dealer()

    def initiate(self, players):
        '''Call dealer to deal cards and bid landlord.

        Args:
            players (list): list of DoudizhuPlayer objects

        '''
        landlord_num = self.dealer.determine_role(players)
        seen_cards = self.dealer.deck[-3:]
        seen_cards.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.seen_cards = cards2str(seen_cards)
        self.landlord_num = landlord_num

    def proceed_round(self, player, action):
        '''
        Call other Classes's functions to keep one round running

        Args:
            player (object): object of DoudizhuPlayer
            action (str): string of legal specific action

        Returns:
            object of DoudizhuPlayer: player who played current biggest cards.
        '''
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
