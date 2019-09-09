# -*- coding: utf-8 -*-
"""Implement Doudizhu Dealer class"""
import random
import functools
import copy
from rlcard.core import Dealer
from rlcard.utils.utils import init_54_deck
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger
from rlcard.games.doudizhu.judger import cards2str


class DoudizhuDealer(Dealer):
    '''Dealer will shuffle, deal cards, and determine players' roles
    '''

    cards_rank = ['3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
                  'A', '2', 'BJ', 'RJ']

    def __init__(self):
        '''Give dealer the deck

        Notes:
            1. deck with 54 cards including black joker and red joker
        '''
        super().__init__()
        self.deck = init_54_deck()
        self.landlord = None

    def shuffle(self):
        random.shuffle(self.deck)

    def deal_cards(self, players):
        '''Deal cards to players

        Args:
            players (list): list of DoudizhuPlayer objects
        '''
        hand_num = (len(self.deck) - 3) // len(players)
        for index, player in enumerate(players):
            player.hand = self.deck[index*hand_num:(index+1)*hand_num]
            player.hand.sort(key=functools.cmp_to_key(doudizhu_sort_card))
            player.remaining_cards = copy.deepcopy(player.hand)

    def determine_role(self, players):
        '''Determine landlord and peasants according to players' hand

        Args:
            players (list): list of DoudizhuPlayer objects

        Returns:
            int: landlord's player_id
        '''
        self.shuffle()
        self.deal_cards(players)
        players[0].role = 'peasant'
        self.landlord = players[0]
        max_score = get_landlord_score(
            cards2str(self.landlord.remaining_cards))
        # print(max_score)
        for player in players[1:]:
            player.role = 'peasant'
            score = get_landlord_score(
                cards2str(player.remaining_cards))
            if score > max_score:
                max_score = score
                self.landlord = player
        self.landlord.role = 'landlord'
        self.landlord.hand.extend(self.deck[-3:])
        self.landlord.hand.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.landlord.remaining_cards = copy.deepcopy(self.landlord.hand)
        return self.landlord.player_id


def doudizhu_sort_card(card_1, card_2):
    '''Sort the cards from the smaller to the greater

    Args:
        card_1 (object): object of Card
        card_2 (object): object of card
    '''
    key = []
    for card in [card_1, card_2]:
        if card.rank == '':
            key.append(DoudizhuDealer.cards_rank.index(card.suit))
        else:
            key.append(DoudizhuDealer.cards_rank.index(card.rank))
    if key[0] > key[1]:
        return 1
    if key[0] < key[1]:
        return -1
    return 0


def get_landlord_score(remaining):
    '''Roughly judge the quality of the hand, and provide a score as basis to
    bid landlord.

    Args:
        remaining (str): string of cards. Eg: '56888TTQKKKAA222R'

    Returns:
        int: score
    '''
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
