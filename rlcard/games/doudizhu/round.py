# -*- coding: utf-8 -*-
''' Implement Doudizhu Round class
'''

import functools

from rlcard.games.doudizhu.dealer import DoudizhuDealer as Dealer
from rlcard.games.doudizhu.judger import cards2str
from rlcard.games.doudizhu.utils import doudizhu_sort_card
from rlcard.games.doudizhu.utils import doudizhu_sort_str


class DoudizhuRound(object):
    ''' Round can call other Classes' functions to keep the game running
    '''

    def __init__(self):
        self.trace = []
        self.played_cards = []

        self.greater_player = None
        self.dealer = Dealer()
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
                       'played_cards': self.played_cards}

    def update_public(self, action):
        ''' Update public trace and played cards

        Args:
            action(str): string of legal specific action
        '''
        self.trace.append((self.current_player, action))
        if action != 'pass':
            self.played_cards.extend(list(action))
            self.played_cards.sort(key=functools.cmp_to_key(doudizhu_sort_str))

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
