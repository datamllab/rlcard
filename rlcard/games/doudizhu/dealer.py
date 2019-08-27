# -*- coding: utf-8 -*-
"""Implement Doudizhu Dealer class"""
import random
import functools
import copy
from rlcard.core import Dealer
from rlcard.utils.utils import init_54_deck
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger


class DoudizhuDealer(Dealer):
    """Dealer can shuffle, deal cards, and determine players' roles
    """

    rank_list = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
                 'A', '2', 'BJ', 'RJ']

    def __init__(self):
        """Give dealer the deck

        Notes:
            deck: 54 cards
        """
        super().__init__()
        self.deck = init_54_deck()
        self.landlord = None

    def shuffle(self):
        random.shuffle(self.deck)

    @staticmethod
    def doudizhu_sort(card_1, card_2):
        """Sort the cards from the smaller to the greater
        """
        key = []
        for card in [card_1, card_2]:
            if card.rank == '':
                key.append(DoudizhuDealer.rank_list.index(card.suit))
            else:
                key.append(DoudizhuDealer.rank_list.index(card.rank))
        if key[0] > key[1]:
            return 1
        if key[0] < key[1]:
            return -1
        return 0

    def deal_cards(self, players):
        """Deal specific number of cards to a specific player

        Args:
            players: a list of Player objects
        """
        hand_num = (len(self.deck) - 3) // len(players)
        for index, player in enumerate(players):
            player.hand = self.deck[index*hand_num:(index+1)*hand_num]
            player.hand.sort(key=functools.cmp_to_key(self.doudizhu_sort))
            player.remaining_cards = copy.deepcopy(player.hand)

    @staticmethod
    def get_landlord_score(remaining):
        score_map = {'A': 1, '2': 2, 'B': 3, 'R': 4}
        score = 0
        # rocket
        if remaining[-2:] == 'BR':
            score += 8
            remaining = remaining[:-2]
        length = len(remaining)
        i = 0
        while i < length:
            # bomb
            if i <= (length - 4) and remaining[i] == remaining[i+3]:
                score += 6
                i += 4
                continue
            # 2, Black Joker, Red Joker
            if remaining[i] in score_map:
                score += score_map[remaining[i]]
            i += 1
        return score

    def determine_role_ii(self, players):
        self.shuffle()
        self.deal_cards(players)
        players[0].role = 'peasant'
        self.landlord = players[0]
        max_score = self.get_landlord_score(
            Judger.cards2str(self.landlord.remaining_cards))
        print(max_score)
        for player in players[1:]:
            player.role = 'peasant'
            score = self.get_landlord_score(
                Judger.cards2str(player.remaining_cards))
            print(score)
            if score > max_score:
                max_score = score
                self.landlord = player
        self.landlord.role = 'landlord'
        for player in players:
            print(Judger.cards2str(player.remaining_cards))
        self.landlord.hand.extend(self.deck[-3:])
        self.landlord.hand.sort(key=functools.cmp_to_key(self.doudizhu_sort))
        self.landlord.remaining_cards = copy.deepcopy(self.landlord.hand)
        for player in players:
            print(Judger.cards2str(player.remaining_cards))
        return self.landlord.player_id

    def determine_role(self, players):
        """Determine landlord and peasants

        Return:
            the number of the landlord among players
        """
        self.shuffle()
        self.deal_cards(players)
        players_num = len(players)
        start = random.randint(0, len(players)-1)
        starter = players[start]
        for offset in range(0, players_num):
            player = players[(start+offset) % players_num]
            actions = player.available_actions()
            # random
            action = random.choice(actions)
            player.play(action)
            if action == 'draw':
                if self.landlord is not None and self.landlord is not starter:
                    self.landlord.role = 'peasant'
                self.landlord = player
        if self.landlord is None:
            for player in players:
                player.role = ''
            return None
        if players[start].role == 'landlord' and self.landlord is not starter:
            players[start].role = ''
            actions = starter.available_actions()
            # random
            action = random.choice(actions)
            starter.play(action)
            if action == 'draw':
                self.landlord.role = 'peasant'
                self.landlord = starter
        self.landlord.hand.extend(self.deck[-3:])
        self.landlord.hand.sort(key=functools.cmp_to_key(self.doudizhu_sort))
        self.landlord.remaining_cards = copy.deepcopy(self.landlord.hand)
        return self.landlord.player_id
