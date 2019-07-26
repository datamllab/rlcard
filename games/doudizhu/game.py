# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
from os import path
sys.path.append(path.dirname(path.dirname(
    path.dirname(path.abspath(__file__)))))
from core import Game
from player import DoudizhuPlayer
from round import DoudizhuRound
from methods import cards2str
from dealer import DoudizhuDealer
from utils.utils import init_54_deck, get_downstream_player_id, get_upstream_player_id
import functools
import random


class DoudizhuGame(Game):
    """Start Doudizhu Game"""
    players_num = 3

    def __init__(self):
        super().__init__()
        self.trace = []
        self.state = {'deck': None, 'seen_cards': None, 'landlord': None,
                      'self': None, 'hand': None, 'trace': self.trace,
                      'remained': None, 'actions': []}
        self.players = [DoudizhuPlayer(num)
                        for num in range(DoudizhuGame.players_num)]
        self.rounder = DoudizhuRound(self.players)
        self.current_player = self.rounder.landlord_num
        player = self.players[self.current_player]
        self.rounder.round_last = get_upstream_player_id(player, self.players)
        deck = init_54_deck()
        deck.sort(key=functools.cmp_to_key(DoudizhuDealer.doudizhu_sort))
        self.state['deck'] = cards2str(deck)
        self.state['landlord'] = self.rounder.landlord_num
        self.state['self'] = self.current_player
        self.state['hand'] = cards2str(player.hand)
        self.state['seen_cards'] = self.rounder.seen_cards
        self.state['remained'] = cards2str(player.remained_cards)
        self.state['actions'] = player.get_playable_cards()

    def start_game(self):
        """Initialize players and round operator, and let round operator
        to proceed round
        """
        player = self.get_player_id()
        state = self.get_state(player)
        while not self.end():
            print(state)
            # random action
            action_num = len(self.state['actions'])
            action = self.state['actions'][random.randint(0, action_num-1)]
            print('action:', action)
            print()
            next_state, next_player = self.step(action)
            self.state = next_state
            player = next_player

    def step(self, action):
        """Perform one draw of the game and return next player's id,
        and the state for next player
        """
        trans = {'10': 'T', 'RJ': 'R', 'BJ': 'B'}
        player = self.players[self.current_player]
        self.trace.append(str(self.current_player)+','+action)
        greater_player = self.rounder.proceed_round(player, action)
        self.rounder.round_last = get_upstream_player_id(
            greater_player, self.players)
        next_player_id = get_downstream_player_id(player, self.players)
        self.state['self'] = next_player_id
        next_player = self.players[next_player_id]
        self.state['hand'] = cards2str(next_player.hand)
        self.state['remained'] = cards2str(next_player.remained_cards)
        if action == 'pass' and self.current_player == self.rounder.round_last:
            self.state['actions'] = next_player.get_playable_cards()
        else:
            gt_cards = next_player.get_gt_cards_dict(greater_player)
            actions = ['pass']
            if gt_cards is not None:
                for type_cards in gt_cards.values():
                    for cards in type_cards:
                        action = ''
                        for card in cards:
                            if card in trans:
                                card = trans[card]
                            action += card
                        actions.append(action)
            self.state['actions'] = actions
        self.current_player = next_player_id
        return self.state, next_player_id

    def get_player_id(self):
        """Return current player's id
        """
        return self.current_player

    def get_player_num(self):
        """Return the number of players in the game
        """
        return DoudizhuGame.players_num

    def get_state(self, player):
        """
        """
        return self.state

    def end(self):
        last_player = get_upstream_player_id(self.players[self.current_player], self.players)
        return len(self.players[last_player].remained_cards) == 0


if __name__ == '__main__':
    GAME = DoudizhuGame()
    GAME.start_game()
