# -*- coding: utf-8 -*-
"""Implement Doudizhu Judger class"""
import json
from os import path
from rlcard.core import Judger
FILE = path.abspath(__file__)
with open(FILE.replace('judger.py', 'card_type.json', 1), 'r') as file:
    CARD_TYPE = json.load(file)


class DoudizhuJudger(Judger):

    @staticmethod
    def cards2str(cards: list):
        """
        Args:
            cards: list of Card class
        Eg:
            cards -> 3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR
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
            remained_cp = remained
            for card in cards:
                if card in remained_cp:
                    remained_cp = remained_cp.replace(card, '', 1)
                else:
                    break
            if (len(remained) - len(remained_cp)) == len(cards):
                playable.append(cards)
        return playable
