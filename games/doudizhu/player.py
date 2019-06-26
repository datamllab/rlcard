# -*- coding: utf-8 -*-
"""Implement Doudizhu Player class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from core import Player
from core import Card
from methods import get_doudizhu_index


class DoudizhuPlayer(Player):
    """
    Player stores cards in the player's hand and the role,
    and can determine the actions can be made according to the rules
    """

    def __init__(self, num):
        """
        Give the player a number in one game
        """
        self.number = num
        self.action = None

    def available_order(self, greater_player=None):
        """
        Get the actions can be made based on the rules

        Return:
            list: a list of available orders
        """
        orders = []
        if hasattr(self, 'role'):
            if greater_player is None:
                orders.append('play')
        else:
            orders.extend(['draw', 'not draw'])
        return orders

    def play(self, action):
        if action == 'not draw':
            self.role = 'farmer'
        elif action == 'draw':
            self.role = 'landlord'

    def print_hand_and_orders(self, greater_player=None):
        print("the hand of player "+str(self.number)+": [", end='')
        for card in self.hand[:-1]:
            print(get_doudizhu_index(card), end=', ')
        print(get_doudizhu_index(self.hand[-1])+']')
        orders = self.available_order(greater_player)
        print("optional operations of player " +
              str(self.number) + ": [", end='')
        for order in orders[:-1]:
            print(order, end=', ')
        print(orders[-1]+']')
        action = input("Your Chioce: ")
        while action not in orders:
            action = input("Please input valid choice: ")
        return action
