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
    '''Determine what cards a player can play'''

    def __init__(self, players):
        self.playable_cards = [CARD_TYPE.copy() for i in range(3)]
        for player in players:
            self.get_playable_cards(player)

    def get_gt_cards(self, player, greater_player):
        '''Provide player's cards which are greater than the ones played by
        previous player in one round

        Args:
            player (DoudizhuPlayer object): the player waiting to play cards
            greater_player (DoudizhuPlayer object): the player who played current biggest cards.

        Returns:
            list: list of string of greater cards

        Note:
            1. return value contains 'pass'
        '''
        gt_cards = ['pass']
        remaining = cards2str(player.remaining_cards)
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
                        if cards not in gt_cards and contains_cards(remaining, cards):
                        # if self.contains_cards(remaining, cards):
                            gt_cards.append(cards)
        return gt_cards

    def get_playable_cards(self, player):
        '''Provide all legal cards the player can play according to his
        remaining cards.

        Args:
            player (DoudizhuPlayer object): object of DoudizhuPlayer

        Returns:
            list: list of string of playable cards
        '''
        player_id = player.player_id
        remaining = cards2str(player.remaining_cards)
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
                if missed in cards or (not contains_cards(remaining, cards)):
                    del self.playable_cards[player_id][cards]
        else:
            for cards in playable_cards:
                if not contains_cards(remaining, cards):
                    del self.playable_cards[player_id][cards]
        return list(self.playable_cards[player_id])


def cards2str(cards: list):
    '''Get the corresponding string representation of cards

    Args:
        cards (list): list of Card objects

    Returns:
        string: string representation of cards
    '''
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


def contains_cards(candidate, target):
    '''Check if cards of candidate contains cards of target.

    Args:
        candidate (string): string represent of cards of candidate
        target (string): string represent of cards of target

    Returns:
        boolean
    '''
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
