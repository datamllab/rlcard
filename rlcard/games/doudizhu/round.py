# -*- coding: utf-8 -*-
''' Implement Doudizhu Round class
'''

import functools
import numpy as np

from rlcard.games.doudizhu import Dealer
from rlcard.games.doudizhu.utils import cards2str, doudizhu_sort_card
from rlcard.games.doudizhu.utils import CARD_RANK_STR, CARD_RANK_STR_INDEX


class DoudizhuRound:
    ''' Round can call other Classes' functions to keep the game running
    '''
    def __init__(self, np_random, played_cards):
        self.np_random = np_random
        self.played_cards = played_cards
        self.trace = []

        self.greater_player = None
        self.dealer = Dealer(self.np_random)
        self.deck_str = cards2str(self.dealer.deck)

    def initiate(self, players):
        ''' Call dealer to deal cards and bid landlord.

        Args:
            players (list): list of DoudizhuPlayer objects
        '''
        landlord_id = self.dealer.determine_role(players)
        seen_cards = self.dealer.deck[-3:]
        seen_cards.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.seen_cards = cards2str(seen_cards)
        self.landlord_id = landlord_id
        self.current_player = landlord_id
        self.public = {'deck': self.deck_str, 'seen_cards': self.seen_cards,
                       'landlord': self.landlord_id, 'trace': self.trace,
                       'played_cards': ['' for _ in range(len(players))]}

    @staticmethod
    def cards_ndarray_to_str(ndarray_cards):
        result = []
        for cards in ndarray_cards:
            _result = []
            for i, _ in enumerate(cards):
                if cards[i] != 0:
                    _result.extend([CARD_RANK_STR[i]] * cards[i])
            result.append(''.join(_result))
        return result

    def update_public(self, action):
        ''' Update public trace and played cards

        Args:
            action(str): string of legal specific action
        '''
        self.trace.append((self.current_player, action))
        if action != 'pass':
            for c in action:
                self.played_cards[self.current_player][CARD_RANK_STR_INDEX[c]] += 1
                if self.current_player == 0 and c in self.seen_cards:
                    self.seen_cards = self.seen_cards.replace(c, '') 
                    self.public['seen_cards'] = self.seen_cards
            self.public['played_cards'] = self.cards_ndarray_to_str(self.played_cards)

    def proceed_round(self, player, action):
        ''' Call other Classes's functions to keep one round running

        Args:
            player (object): object of DoudizhuPlayer
            action (str): string of legal specific action

        Returns:
            object of DoudizhuPlayer: player who played current biggest cards.
        '''
        self.update_public(action)
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player

    def step_back(self, players):
        ''' Reverse the last action

        Args:
            players (list): list of DoudizhuPlayer objects
        Returns:
            The last player id and the cards played
        '''
        player_id, cards = self.trace.pop()
        self.current_player = player_id
        if (cards != 'pass'):
            for card in cards:
                # self.played_cards.remove(card)
                self.played_cards[player_id][CARD_RANK_STR_INDEX[card]] -= 1
            self.public['played_cards'] = self.cards_ndarray_to_str(self.played_cards)
        greater_player_id = self.find_last_greater_player_id_in_trace()
        if (greater_player_id is not None):
            self.greater_player = players[greater_player_id]
        else:
            self.greater_player = None
        return player_id, cards

    def find_last_greater_player_id_in_trace(self):
        ''' Find the last greater_player's id in trace

        Returns:
            The last greater_player's id in trace
        '''
        for i in range(len(self.trace) - 1, -1, -1):
            _id, action = self.trace[i]
            if (action != 'pass'):
                return _id
        return None

    def find_last_played_cards_in_trace(self, player_id):
        ''' Find the player_id's last played_cards in trace

        Returns:
            The player_id's last played_cards in trace
        '''
        for i in range(len(self.trace) - 1, -1, -1):
            _id, action = self.trace[i]
            if (_id == player_id and action != 'pass'):
                return action
        return None
