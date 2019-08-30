# -*- coding: utf-8 -*-
"""Implement Texasholdem Round class"""
import functools
from rlcard.core import Round
from rlcard.games.simpletexasholdem.dealer import SimpleTexasDealer as Dealer
from rlcard.games.simpletexasholdem.judger import SimpleTexasJudger as Judger


class SimpleTexasRound(Round):

    def __init__(self, players):
        """
        initialize the game, 

        Args:
            players: a list of Player objects

        Notes:
            greater_player: the winner in one round
            dealer: a instance of DouzizhuDealer
            seen_cards: cards given to landlord after determining landlord
            landlord_num: the id of landlord
        """
        self.greater_player = None
        self.dealer = Dealer()
  
        seen_cards = self.dealer.deck[-3:]
        seen_cards.sort(key=functools.cmp_to_key(Dealer.texas_sort))
        # self.seen_cards = Judger.cards2str(seen_cards)
        # print('seen cards:', self.seen_cards)

    def proceed_round(self, player, action):
        """
        Call other Classes's functions to keep one round running
        """
        self.greater_player = player.play(action, self.greater_player)
        return self.greater_player
