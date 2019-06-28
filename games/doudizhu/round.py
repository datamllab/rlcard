# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import sys
from os import path
from core import Round
from dealer import DoudizhuDealer
from methods import get_doudizhu_index


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
        """
        self.greater_player = None
        self.round_id = 0
        self.dealer = DoudizhuDealer()
        while True:
            landlord_num = self.dealer.determine_role(players)
            if landlord_num is not None:
                break
        print('###############')
        for player in players:
            print(str(player.number)+player.role)
            print("the hand: [", end='')
            for card in player.hand[:-1]:
                print(get_doudizhu_index(card), end=', ')
            print(get_doudizhu_index(player.hand[-1])+']')
        print('###############')
        print('The number of the landlord is '+str(landlord_num))
        self.landlord_num = landlord_num

    def proceed_round(self, players, start):
        """
        Call other Classes's functions to keep one round running

        Args:
            players: a list of players
            start: The number of the first player to play in one round
                   (landlord or winner in last round)
        Return:
            tuple: (1(if game over)/0(if not),
                   the number of the winner in this round)       
        """
        self.round_id += 1
        print('\nRound '+str(self.round_id))
        players_num = len(players)
        for offset in range(0, players_num):
            player = players[(start+offset) % players_num]
            action = player.print_hand_and_orders(self.greater_player)
            self.greater_player = player.play(action, self.greater_player)
            if len(player.hand) == 0:
                return 1, player.number
        return 0, self.greater_player.number
