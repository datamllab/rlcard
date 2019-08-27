# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
import functools
import random
import numpy as np
from os import path
FILE = path.abspath(__file__)
sys.path.append(path.dirname(path.dirname(path.dirname(path.dirname(FILE)))))
from rlcard.core import Game
from rlcard.games.doudizhu.player import DoudizhuPlayer as Player
from rlcard.games.doudizhu.round import DoudizhuRound as Round
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger
from rlcard.games.doudizhu.dealer import DoudizhuDealer as Dealer
from rlcard.utils.utils import init_54_deck
from rlcard.utils.utils import get_downstream_player_id, get_upstream_player_id


class DoudizhuGame(Game):
    """Start Doudizhu Game"""
    players_num = 3
    game_result = {0: 0, 1: 0, 2: 0}
    char_list = ['3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K',
                 'A', '2', 'B', 'R']

    def __init__(self, seed=None):
        """Initialize players and state

        A example of state:
            {
             'deck': '3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR',
             'cards_seen': 'QA2',
             'landlord': 1,
             'self': 1,
             'hand': '34455678TTJQKAAA222R',
             'trace': [(1, '8222'), (2, 'pass'), (0, 'pass'), (1, '55'),
                       (2, 'pass'), (0, '88'), (1, 'TT'), (2, 'JJ'),
                       (0, 'pass'), (1, 'pass'), (2, '45678'), (0, 'pass'),
                       (1, 'pass'), (2, '5'), (0, 'K')],
            'remaining': '34467JQKAAAR',
            'actions': ['pass', 'A', 'R']
            }
        """
        super().__init__()
        self.set_seed(seed)
        self.trace = []
        self.cards_played = []
        self.state = {'deck': None, 'cards_seen': None, 'landlord': None,
                      'self': None, 'hand': None, 'trace': self.trace,
                      'cards_played': None, 'cards_others': None,
                      'remaining': None, 'actions': []}
        self.players = [Player(num)
                        for num in range(DoudizhuGame.players_num)]
        self.rounder = Round(self.players)
        self.judger = Judger(self.players)
        self.current_player = self.rounder.landlord_num
        player = self.players[self.current_player]
        self.rounder.round_last = get_upstream_player_id(player, self.players)
        deck = init_54_deck()
        deck.sort(key=functools.cmp_to_key(Dealer.doudizhu_sort))
        self.state['deck'] = Judger.cards2str(deck)
        self.state['landlord'] = self.rounder.landlord_num
        self.state['self'] = self.current_player
        self.state['hand'] = Judger.cards2str(player.hand)
        self.state['cards_seen'] = self.rounder.cards_seen
        self.state['remaining'] = Judger.cards2str(player.remaining_cards)
        self.state['cards_others'] = self.get_others_remaining(player)
        self.state['actions'] = list(
            self.judger.playable_cards[self.current_player])

    def set_seed(self, seed):
        random.seed(seed)
        print('############ Doudizhu seeded('+str(seed)+') ############')

    def start_game(self):
        """
        Run a complete game by randomly choosing an action
        """
        player = self.get_player_id()
        state = self.get_state(player)
        while not self.end():
            print(state)
            print(self.encoder(state))
            self.test_state(self.encoder(state))
            # random action
            action_num = len(self.state['actions'])
            action = self.state['actions'][random.randint(0, action_num-1)]
            print('action:', action)
            next_state, next_player = self.step(action)
            self.state = next_state
            player = next_player
        print('#####Final states#####')
        for player_id in range(DoudizhuGame.players_num):
            state = self.get_state(player_id)
            print(state)
            state_encoded = self.encoder(state)
            print(state_encoded)
            self.test_state(state_encoded)

    def step(self, action):
        """Perform one draw of the game and return next player's id,
        and the state for next player
        """
        player = self.players[self.current_player]
        self.trace.append((self.current_player, action))
        if action != 'pass':
            self.add_cards_played(action)
            self.state['cards_played'] = self.cards_played
        greater_player = self.rounder.proceed_round(player, action)
        next_player_id = get_downstream_player_id(player, self.players)
        self.state['self'] = next_player_id
        next_player = self.players[next_player_id]
        self.state['hand'] = Judger.cards2str(next_player.hand)
        self.state['remaining'] = Judger.cards2str(next_player.remaining_cards)
        actions = next_player.available_actions(greater_player, self.judger)
        self.state['actions'] = actions
        self.state['cards_others'] = self.get_others_remaining(next_player)
        self.current_player = next_player_id
        return self.state, next_player_id

    def encoder(self, state):
        response = np.zeros((6, 15), dtype=int)
        self.update_array(response[0], state['remaining'])
        self.update_array(response[1], state['cards_others'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                self.update_array(response[4-i], action[1])
        if state['cards_played'] is not None:
            self.update_array(response[5], state['cards_played'])
        return response

    @staticmethod
    def update_array(array, cards):
        for card in cards:
            rank = DoudizhuGame.char_list.index(card)
            array[rank] += 1

    def get_others_remaining(self, player):
        player_up = self.players[get_upstream_player_id(player, self.players)]
        player_down = self.players[get_downstream_player_id(
            player, self.players)]
        cards_others = (player_up.remaining_cards +
                        player_down.remaining_cards)
        cards_others.sort(key=functools.cmp_to_key(Dealer.doudizhu_sort))
        return Judger.cards2str(cards_others)

    @staticmethod
    def doudizhu_sort(card_1, card_2):
        key_1 = DoudizhuGame.char_list.index(card_1)
        key_2 = DoudizhuGame.char_list.index(card_2)
        if key_1 > key_2:
            return 1
        if key_1 < key_2:
            return -1
        return 0

    def add_cards_played(self, action):
        self.cards_played.extend(list(action))
        self.cards_played.sort(key=functools.cmp_to_key(self.doudizhu_sort))

    def get_player_id(self):
        """Return current player's id
        """
        return self.current_player

    def get_player_num(self):
        """Return the number of players in the game
        """
        return DoudizhuGame.players_num

    def get_state(self, player_id):
        """Return player's state
        """
        player = self.players[player_id]
        if self.current_player is not None:  # when get first state
            return self.state
        else:  # when get final states of all players
            self.state['self'] = player_id
            self.state['hand'] = Judger.cards2str(player.hand)
            self.state['remaining'] = Judger.cards2str(player.remaining_cards)
            self.state['actions'] = None
            self.state['cards_others'] = self.get_others_remaining(player)
            return self.state

    def is_winner(self, player_id):
        """Return 1(winner), 0(not winner)

        Note:
            Only can be used after game ending
        """
        return DoudizhuGame.game_result[player_id]

    def end(self):
        """Return whether the game has been over
        """
        if self.current_player is None:
            return 1
        last_player = get_upstream_player_id(
            self.players[self.current_player], self.players)
        if len(self.players[last_player].remaining_cards) == 0:
            if self.players[last_player].role == 'peasant':
                for _, player in enumerate(self.players):
                    if player.role == 'peasant':
                        DoudizhuGame.game_result[_] = 1
            else:
                DoudizhuGame.game_result[last_player] = 1
            self.current_player = None
            return 1
        return 0

    @staticmethod
    def test_state(state_encoded):
        if state_encoded[0][-1]+state_encoded[1][-1]+state_encoded[-1][-1] != 1:
            input('RJ error')
        if state_encoded[0][-2]+state_encoded[1][-2]+state_encoded[-1][-2] != 1:
            input('BJ error')
        state = zip(state_encoded[0][:-2],
                    state_encoded[1][:-2], state_encoded[-1][:-2])
        for remaining, others, played in state:
            if (remaining+others+played) != 4:
                input('error')


if __name__ == '__main__':
    # random test
    GAME = DoudizhuGame()
    GAME.start_game()
