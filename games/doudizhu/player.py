# -*- coding: utf-8 -*-
"""Implement Doudizhu Player class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(
    path.dirname(path.abspath(__file__)))))
from core import Player
from methods import check_play_cards, get_play_string, cards2str, index2str, get_doudizhu_index
from doudizhu import Card as DoudizhuCard
from doudizhu import check_card_type, list_greater_cards, cards_greater
from doudizhu import Doudizhu
from dealer import DoudizhuDealer as Dealer


class DoudizhuPlayer(Player):
    """Player can store cards in the player's hand and the role,
    determine the actions can be made according to the rules,
    and can perfrom responding action
    """

    def __init__(self, num):
        """Give the player a number(not id) in one game

        Member Vars:
            player_id: a player's id in one game
            role: a player's temporary role in one game(landlord or farmer)
            played_cards: the cards played in one round
        """
        self.player_id = num
        # self.role = None
        self.hand = []
        self.remained_cards = []
        self.role = ''
        self.played_cards = None

    def available_order(self, greater_player=None):
        """Get the actions can be made based on the rules

        Args:
            greater_player: the current winner in this round

        Return:
            list: a list of available orders
                  (some of ['draw'(叫/抢地主), 'not draw', 'play(出牌)', 'pass'])
        """
        orders = []
        if self.role != '':
            if greater_player is None or greater_player is self:
                orders.append('play')
                playable = self.get_playable_cards()
            else:
                orders.append('pass')
                candidate = get_play_string(
                    self.remained_cards, range(len(self.remained_cards)))
                candidate = DoudizhuCard.card_ints_from_string(candidate)
                greater_cards_lists = list_greater_cards(
                    greater_player.played_cards, candidate)
                if len(greater_cards_lists) > 0:
                    gt_dict = self.get_gt_cards_dict(greater_player)
                    print('playable cards: ')
                    print(gt_dict)
                    orders.append('play')
        else:
            orders.extend(['draw', 'not draw'])
        return orders

    def get_gt_cards_dict(self, greater_player):
        candidate = get_play_string(
            self.remained_cards, range(len(self.remained_cards)))
        candidate = DoudizhuCard.card_ints_from_string(candidate)
        greater_cards_lists = list_greater_cards(
            greater_player.played_cards, candidate)
        if len(greater_cards_lists) > 0:
            gt_cards = {}
            for card_type, cards_list in greater_cards_lists.items():
                gt_card_list = []
                for card_ints in cards_list:
                    cards_list = []
                    for card_int in card_ints:
                        rank_int = DoudizhuCard.get_rank_int(card_int)
                        cards_list.append(Dealer.rank_list[rank_int])
                    gt_card_list.append(cards_list)
                gt_cards[card_type] = gt_card_list
            return gt_cards
        else:
            return None

    def get_playable_cards(self):
        """
        """
        playable = []
        cards_dict = Doudizhu.DATA
        remained = cards2str(self.remained_cards)
        for cards in cards_dict:
            remained_cp = remained
            cards = index2str(cards.split('-'))
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

        Args:
            action: one of ['draw'(叫/抢地主), 'not draw', 'play(出牌)', 'pass']
            greater_player: the same to the upper

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
            play_cards = ''
            for play_card in action:
                if play_card in trans:
                    play_card = trans[play_card]
                for _, remain_card in enumerate(self.remained_cards):
                    if remain_card.rank != '':
                        remain_card = remain_card.rank
                    else:
                        remain_card = remain_card.suit
                    if play_card == remain_card:
                        play_cards += (get_doudizhu_index(
                            self.remained_cards[_]) + '-')
                        self.remained_cards.remove(self.remained_cards[_])
                        break
            self.played_cards = DoudizhuCard.card_ints_from_string(
                play_cards[:-1])
            return self

    def print_remained_card(self):
        """print the remained cards
        """
        remained_cards = [str(index)+':'+card.get_index()
                          for index, card in enumerate(self.remained_cards)]
        print('the remained cards of player '+str(self.player_id) +
              '('+self.role+')'+':', remained_cards)

    def print_remained_and_orders(self, greater_player=None):
        """Print_remained_and_orders

        Args:
            greater_player: the same to the upper

        Return:
            The action choosed by player according to optional operations
        """
        print()
        self.print_remained_card()
        orders = self.available_order(greater_player)
        print("optional actions of player " +
              str(self.player_id) + ":", orders)
        return orders
        '''action = input("Your Choice: ")
        while action not in orders:
            action = input("Please input valid choice: ")
        return action'''
