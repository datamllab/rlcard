# -*- coding: utf-8 -*-
"""Implement Doudizhu Player class"""
import json
from os import path
from rlcard.core import Player
from rlcard.games.doudizhu.methods import cards2str
FILE = path.abspath(__file__)
with open(FILE.replace('player.py', 'card_type.json', 1), 'r') as file:
    CARD_TYPE = json.load(file)


class DoudizhuPlayer(Player):
    """Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom responding action
    """

    def __init__(self, player_id):
        """Give the player a number(not id) in one game

        Notes:
            role: a player's temporary role in one game(landlord or farmer)
            played_cards_ii: the cards played in one round
            hand: initial hand; don't change
            remained_cards: The rest of the cards after playing some of them
        """
        self.player_id = player_id
        self.hand = []
        self.remained_cards = []
        self.role = ''
        self.played_cards_ii = None

    def available_actions(self, greater_player=None):
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
                actions = self.get_playable_cards_ii()
            else:
                actions = self.get_gt_cards(greater_player)
        else:
            actions.extend(['draw', 'not draw'])
        return actions

    def get_gt_cards(self, greater_player):
        gt_cards = ['pass']
        target_cards = greater_player.played_cards_ii
        target_types = CARD_TYPE[target_cards]
        type_dict = {}
        for card_type, weight in target_types:
            if card_type not in type_dict:
                type_dict[card_type] = weight
        if 'rocket' in type_dict:
            return gt_cards
        type_dict['rocket'] = -1
        if 'bomb' not in type_dict:
            type_dict['bomb'] = -1
        playable_cards = self.get_playable_cards_ii()
        for cards in playable_cards:
            candidate_types = CARD_TYPE[cards]
            for card_type, weight in candidate_types:
                if card_type in type_dict and weight > type_dict[card_type]:
                    gt_cards.append(cards)
                    break
        return gt_cards

    def get_playable_cards_ii(self):
        playable = []
        remained = cards2str(self.remained_cards)
        for cards in CARD_TYPE:
            remained_cp = remained
            for card in cards:
                if card in remained_cp:
                    remained_cp = remained_cp.replace(card, '', 1)
                else:
                    break
            if (len(remained) - len(remained_cp)) == len(cards):
                playable.append(cards)
        return playable

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
            self.played_cards_ii = action
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
            return self

    def print_remained_card(self):
        remained_cards = [str(index)+':'+card.get_index()
                          for index, card in enumerate(self.remained_cards)]
        print('the remained cards of player '+str(self.player_id) +
              '('+self.role+')'+':', remained_cards)

    def print_remained_and_actions(self, greater_player=None):
        print()
        self.print_remained_card()
        actions = self.available_actions(greater_player)
        print("optional actions of player " +
              str(self.player_id) + ":", actions)
        return actions
