# -*- coding: utf-8 -*-
"""Implement Doudizhu Judger class"""
from rlcard.core import Judger
from rlcard.games.doudizhu.utils import CARD_TYPE, TYPE_CARD
from rlcard.games.doudizhu.utils import cards2str, contains_cards


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
        # add 'pass' to legal actions
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
