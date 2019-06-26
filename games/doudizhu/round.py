# -*- coding: utf-8 -*-
"""Implement Doudizhu Round class"""
import sys
import random
from os import path
sys.path.append(path.dirname(path.dirname(
    path.dirname(path.abspath(__file__)))))
from core import Round
from dealer import DoudizhuDealer


class DoudizhuRound(Round):
    """
    Round stores the id the ongoing round
    and can call other Classes' functions to keep the game running
    """

    def __init__(self, players):
        """
        Args:
            players: a list of Player objects
        """
        self.greater_player = None
        self.round_id = 0
        self.dealer = DoudizhuDealer()
        landlord_num = self.dealer.determine_role(players)
        print('###############')
        for player in players:
            print(str(player.number)+player.role)
            print("the hand: [", end='')
            for card in player.hand[:-1]:
                print(card.get_index(), end=', ')
            print(player.hand[-1].get_index()+']')
        print('###############')
        print('The number of landlord is '+str(landlord_num))
        self.proceed_round(players, landlord_num)

    def proceed_round(self, players, start):
        """
        Call other Classes's functions to keep the game running

        Args:
            players: a list of players
            start: The number of the first player to play in every round
        """
        self.round_id += 1
        players_num = len(players)
        for offset in range(0, players_num):
            player = players[(start+offset) % players_num]
            action = player.print_hand_and_orders(self.greater_player)
            if action == 'play':
                print('Choose your cards: ')
