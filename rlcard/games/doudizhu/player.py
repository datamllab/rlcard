# -*- coding: utf-8 -*-
"""Implement Doudizhu Player class"""
import json
from os import path
from rlcard.core import Player
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger
# import time


class DoudizhuPlayer(Player):
    """Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom responding action
    """

    def __init__(self, player_id):
        """Give the player a number(not id) in one game

        Notes:
            role: a player's temporary role in one game(landlord or farmer)
            played_cards: the cards played in one round
            hand: initial hand; don't change
            remained_cards: The rest of the cards after playing some of them
        """
        self.player_id = player_id
        self.hand = []
        self.remained_cards = []
        self.role = ''
        self.played_cards = None
        self.singles = '3456789TJQKA2BR'

    def available_actions(self, greater_player=None, judger=None):
        """Get the actions can be made based on the rules

        Args:
            greater_player: the current winner in this round

        Return:
            list: a list of available orders
                  Eg: ['pass', '8', '9', 'T', 'J']
        """
        actions = []
        if self.role != '':
            if greater_player is None or greater_player is self:
                # actions_ii = self.judger.get_playable_cards(self)
                actions = judger.get_playable_cards_ii(self)
                '''
                for action, action_ii in zip(actions, actions_ii):
                    if action != action_ii:
                        input('cyp0817 get_playable_actions_ii wrong')
                '''
            else:
                actions = judger.get_gt_cards_ii(self, greater_player)
        else:
            actions.extend(['draw', 'not draw'])
        return actions

    def play(self, action, greater_player=None):
        """Perfrom action

        Return:
            if current winner changed, return current winner
            else return None
        """
        trans = {'T': '10', 'B': 'BJ', 'R': 'RJ'}
        if action == 'not draw':
            self.role = 'farmer'
            return None
        if action == 'draw':
            self.role = 'landlord'
            return None
        if action == 'pass':
            return greater_player
        else:
            # time_start = time.time()
            self.played_cards = action
            for play_card in action:
                if play_card in trans:
                    play_card = trans[play_card]
                for _, remain_card in enumerate(self.remained_cards):
                    if remain_card.rank != '':
                        remain_card = remain_card.rank
                    else:
                        remain_card = remain_card.suit
                    if play_card == remain_card:
                        self.remained_cards.remove(self.remained_cards[_])
                        break
                # time_end = time.time()
                # print('play cost', time_end-time_start)
            return self

    def print_remained_card(self):
        remained_cards = [str(index)+':'+card.get_index()
                          for index, card in enumerate(self.remained_cards)]
        print('remained cards of player '+str(self.player_id) +
              '('+self.role+')'+':', remained_cards)

    def print_remained_and_actions(self, greater_player=None):
        print()
        self.print_remained_card()
        actions = self.available_actions(greater_player)
        print("optional actions of player " +
              str(self.player_id) + ":", actions)
        return actions
