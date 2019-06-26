# -*- coding: utf-8 -*-
"""Implement Doudizhu Dealer class"""
import sys
import random
import functools
from os import path
sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))
from core import Dealer
from utils.utils import init_54_deck


class DoudizhuDealer(Dealer):

    rank_list = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
                 'A', '2', 'BJ', 'RJ']

    def __init__(self):
        """
        The dealer should have all the cards at the beginning of a game
        """
        super().__init__()
        self.deck = init_54_deck()
        self.landlord = None

    def shuffle(self):
        random.shuffle(self.deck)

    @staticmethod
    def doudizhu_sort(card_A, card_B):
        key = []
        for card in [card_A, card_B]:
            if card.rank == '':
                key.append(DoudizhuDealer.rank_list.index(card.suit))
            else:
                key.append(DoudizhuDealer.rank_list.index(card.rank))
        if key[0] > key[1]:
            return -1
        if key[0] < key[1]:
            return 1
        return 0

    def deal_cards(self, players):
        """
        Deal specific number of cards to a specific player

        Args:
            players: a list of Player objects
        """
        hand_num = (len(self.deck) - 3) // len(players)
        for index, player in enumerate(players):
            player.hand = self.deck[index*hand_num:(index+1)*hand_num]
            player.hand.sort(key=functools.cmp_to_key(self.doudizhu_sort))

    def determine_role(self, players):
        """
        Determine landlord and farmers

        return:
            the landlord among players
        """
        self.shuffle()
        self.deal_cards(players)
        players_num = len(players)
        start = random.randint(0, len(players)-1)
        starter = players[start]
        for offset in range(0, players_num):
            player = players[(start+offset) % players_num]
            action = player.print_hand_and_orders()
            player.play(action)
            if action == 'draw':
                if self.landlord is not None and self.landlord is not starter:
                    self.landlord.role = 'farmer'
                self.landlord = player
        if self.landlord is None:
            for player in players:
                delattr(player, 'role')
            self.determine_role(players)
        if players[start].role == 'landlord' and self.landlord is not starter:
            delattr(starter, 'role')
            action = starter.print_hand_and_orders()
            starter.play(action)
            if action == 'draw':
                self.landlord.role = 'farmer'
                self.landlord = starter
        self.landlord.hand.extend(self.deck[-3:])
        self.landlord.hand.sort(key=functools.cmp_to_key(self.doudizhu_sort))
        return self.landlord.number


if __name__ == '__main__':
    dealer = DoudizhuDealer()