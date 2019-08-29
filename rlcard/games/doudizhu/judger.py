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
        Get player's cards which are greater than the ones played by
        previous player(current greater_player)

        Note: response contains 'pass'
        """
        gt_cards = ['pass']
        remaining = self.cards2str(player.remaining_cards)
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
        for card_type, weight in type_dict.items():
            candidate = TYPE_CARD[card_type]
            for can_weight, cards_list in candidate.items():
                if int(can_weight) > weight:
                    for cards in cards_list:
                        # TODO: improve efficiency
                        if cards not in gt_cards and self.contains_cards(remaining, cards):
                        # if self.contains_cards(remaining, cards):
                            gt_cards.append(cards)
        return gt_cards

    def get_playable_cards_ii(self, player):
        player_id = player.player_id
        remaining = self.cards2str(player.remaining_cards)
        missed = None
        for single in player.singles:
            if single not in remaining:
                missed = single
                break
        playable_cards = list(self.playable_cards[player_id])
        if missed is not None:
            position = player.singles.find(missed)
            player.singles = player.singles[position+1:]
            for cards in playable_cards:
                if missed in cards or (not self.contains_cards(remaining, cards)):
                    del self.playable_cards[player_id][cards]
        else:
            for cards in playable_cards:
                if not self.contains_cards(remaining, cards):
                    del self.playable_cards[player_id][cards]
        return list(self.playable_cards[player_id])
