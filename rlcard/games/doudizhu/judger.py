# -*- coding: utf-8 -*-
"""Implement Doudizhu Judger class"""
import json
from os import path
from rlcard.core import Judger
FILE = path.abspath(__file__)
with open(FILE.replace('judger.py', 'card_type.json', 1), 'r') as file:
    CARD_TYPE = json.load(file)
with open(FILE.replace('judger.py', 'type_card.json', 1), 'r') as file:
    TYPE_CARD = json.load(file)
import time


class DoudizhuJudger(Judger):

    def __init__(self, players):
        self.playable_cards = [CARD_TYPE.copy() for i in range(3)]
        for player in players:
            self.get_playable_cards_ii(player)
            

    @staticmethod
    def cards2str(cards: list):
        """
        Args:
            cards: list of Card class
        Eg:
            deck -> 3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR
        """
        response = ''
        for card in cards:
            if card.rank == '':
                response += card.suit[0]
            else:
                if card.rank == '10':
                    response += 'T'
                else:
                    response += card.rank
        return response

    @staticmethod
    def contains_cards(candidate, target):
        len_can = len(candidate)
        len_tar = len(target)
        if len_can < len_tar:
            return False
        if len_can == len_tar:
            if candidate == target:
                return True
            return False
        beg = 0
        for tar_card in target:
            beg = candidate.find(tar_card, beg) + 1
            if beg == 0:
                return False
        return True

    def get_gt_cards_ii(self, player, greater_player):
        """
        advanced
        """
        # time_start = time.time()
        gt_cards = ['pass']
        remained = self.cards2str(player.remained_cards)
        target_cards = greater_player.played_cards
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
        
        # iii
        playable = self.playable_cards[player.player_id]
        for cards, type_weights in playable.items():
            for type_weight in type_weights:
                if type_weight[0] in type_dict and type_weight[1] > type_dict[type_weight[0]]:
                    gt_cards.append(cards)
                    break
        # time_end = time.time()
        # print('playable cost', time_end-time_start)
        '''
        for card_type, weight in type_dict.items():
            candidate = TYPE_CARD[card_type]
            for can_weight, cards_list in candidate.items():
                if int(can_weight) > weight:
                    for cards in cards_list:
                        #if self.contains_cards(remained, cards):
                        if cards in self.playable_cards[player.player_id]:
                            gt_cards.append(cards)
        gt_cards = list(set(gt_cards))
        '''
        return gt_cards

    def get_gt_cards(self, player, greater_player):
        """Get player's cards which are greater than the ones played by
        previous player(current greater_player)

        Note: response contains 'pass'
        """
        gt_cards = ['pass']
        target_cards = greater_player.played_cards
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
        playable_cards = self.get_playable_cards(player)
        for cards in playable_cards:
            candidate_types = CARD_TYPE[cards]
            for card_type, weight in candidate_types:
                if card_type in type_dict and weight > type_dict[card_type]:
                    gt_cards.append(cards)
                    break
        return gt_cards

    def get_playable_cards(self, player):
        playable = []
        remained = self.cards2str(player.remained_cards)
        for cards in CARD_TYPE:
            if self.contains_cards(remained, cards):
                playable.append(cards)
        return playable

    def get_playable_cards_ii(self, player):
        # time_start = time.time()
        player_id = player.player_id
        remained = self.cards2str(player.remained_cards)
        missed = None
        for single in player.singles:
            if single not in remained:
                missed = single
                break
        playable_cards = list(self.playable_cards[player_id])
        if missed is not None:
            position = player.singles.find(missed)
            player.singles = player.singles[position+1:]
            for cards in playable_cards:
                if missed in cards or (not self.contains_cards(remained, cards)):
                    del self.playable_cards[player_id][cards]
        else:
            for cards in playable_cards:
                if not self.contains_cards(remained, cards):
                    del self.playable_cards[player_id][cards]
        '''
        singles = '3456789TJQK'
        miss_card = ''
        for single in singles:
            if single not in remained:
                miss_card += single
                if len(miss_card) == 2:
                    break
        print(miss_card)
        if miss_card == '':
            for cards in CARD_TYPE:
                if self.contains_cards(remained, cards):
                    playable.append(cards)
        else:
            for cards in CARD_TYPE:
                if miss_card[0] in cards or miss_card[1] in cards:
                    continue
                if self.contains_cards(remained, cards):
                    playable.append(cards)
        '''
        # time_end = time.time()
        # print('playable cost', time_end-time_start)
        # print(player.player_id, len(self.playable_cards[player_id]))
        return list(self.playable_cards[player_id])
