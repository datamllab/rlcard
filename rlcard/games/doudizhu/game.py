# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import sys
import functools
import random
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

    def __init__(self, seed=None):
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
        self.set_seed(seed)
        self.trace = []
        self.state = {'deck': None, 'seen_cards': None, 'landlord': None,
                      'self': None, 'hand': None, 'trace': self.trace,
                      'remained': None, 'actions': []}
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
        self.state['seen_cards'] = self.rounder.seen_cards
        self.state['remained'] = Judger.cards2str(player.remained_cards)
        self.state['actions'] = list(self.judger.playable_cards[self.current_player])

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
            # random action
            action_num = len(self.state['actions'])
            action = self.state['actions'][random.randint(0, action_num-1)]
            print('action:', action)
            print()
            next_state, next_player = self.step(action)
            self.state = next_state
            player = next_player

        print('#####Final states#####')
        for player_id in range(DoudizhuGame.players_num):
            print(self.get_state(player_id), '\n')

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
        self.state['hand'] = Judger.cards2str(next_player.hand)
        self.state['remained'] = Judger.cards2str(next_player.remained_cards)
        actions = next_player.available_actions(greater_player, self.judger)
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

    def get_state(self, player_id):
        """Return player's state
        """
        player = self.players[player_id]
        if self.current_player is not None:  # when get first state
            return self.state
        else:  # when get final states of all players
            self.state['self'] = player_id
            self.state['hand'] = Judger.cards2str(player.hand)
            self.state['remained'] = Judger.cards2str(player.remained_cards)
            self.state['actions'] = None
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
        if len(self.players[last_player].remained_cards) == 0:
            if self.players[last_player].role == 'farmer':
                for _, player in enumerate(self.players):
                    if player.role == 'farmer':
                        DoudizhuGame.game_result[_] = 1
            else:
                DoudizhuGame.game_result[last_player] = 1
            self.current_player = None
            return 1
        return 0


if __name__ == '__main__':
    # random test
    GAME = DoudizhuGame()
    GAME.start_game()
