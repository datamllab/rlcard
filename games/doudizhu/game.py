# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
import functools
import random
from os import path
FILE = path.abspath(__file__)
sys.path.append(path.dirname(path.dirname(path.dirname(FILE))))
from core import Game
from player import DoudizhuPlayer
from round import DoudizhuRound
from methods import cards2str
from dealer import DoudizhuDealer
from utils.utils import init_54_deck
from utils.utils import get_downstream_player_id, get_upstream_player_id


class DoudizhuGame(Game):
    """Start Doudizhu Game"""
    players_num = 3

    def __init__(self):
        """Initialize players and state

        A example of state:
            {
             'deck': '3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR',
             'seen_cards': 'QA2',
             'landlord': 1,
             'self': 1,
             'hand': '34455678TTJQKAAA222R',
             'trace': [(1, '8222'), (2, 'pass'), (0, 'pass'), (1, '55'),
                       (2, 'pass'), (0, '88'), (1, 'TT'), (2, 'JJ'),
                       (0, 'pass'), (1, 'pass'), (2, '45678'), (0, 'pass'),
                       (1, 'pass'), (2, '5'), (0, 'K')],
            'remained': '34467JQKAAAR',
            'actions': ['pass', 'A', 'R']
            }
        """
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
        self.state['actions'] = player.get_playable_cards_ii()

    def start_game(self):
        """
        Run a complete game by randomly choosing an action
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
        player = self.players[self.current_player]
        self.trace.append((self.current_player, action))
        greater_player = self.rounder.proceed_round(player, action)
        next_player_id = get_downstream_player_id(player, self.players)
        self.state['self'] = next_player_id
        next_player = self.players[next_player_id]
        self.state['hand'] = cards2str(next_player.hand)
        self.state['remained'] = cards2str(next_player.remained_cards)
        actions = next_player.available_actions(greater_player)
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
        """Return player's state
        """
        return self.state

    def end(self):
        """Return whether the game has been over
        """
        last_player = get_upstream_player_id(
            self.players[self.current_player], self.players)
        return len(self.players[last_player].remained_cards) == 0


if __name__ == '__main__':
    # random test
    GAME = DoudizhuGame()
    GAME.start_game()
