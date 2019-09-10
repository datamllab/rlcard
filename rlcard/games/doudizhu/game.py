# -*- coding: utf-8 -*-
"""Implement Doudizhu Game class"""
import functools
import copy
from rlcard.core import Game
from rlcard.games.doudizhu.judger import cards2str
from rlcard.games.doudizhu.player import DoudizhuPlayer as Player
from rlcard.games.doudizhu.round import DoudizhuRound as Round
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger
from rlcard.games.doudizhu.utils import doudizhu_sort_str, doudizhu_sort_card
from rlcard.utils.utils import init_54_deck
from rlcard.utils.utils import get_downstream_player_id, get_upstream_player_id


class DoudizhuGame(Game):
    '''Provide game APIs for env to run doudizhu and get corresponding state 
    information.

    An example of state during runtime:
            {
             'deck': '3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR',
             'cards_seen': 'TQA',
             'landlord': 0,
             'self': 2,
             'hand': '3456677799TJQKAAB',
             'trace': [(0, '8222'), (1, 'pass'), (2, 'pass'), (0, '6KKK'),
                       (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')],
             'cards_played': ['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2'],
             'cards_others': '333444555678899TTTJJJQQAA2R',
             'remaining': '3456677799TJQKAAB',
             'actions': ['pass', 'K', 'A', 'B']
            }
    '''
    players_num = 3

    def __init__(self):
        self.current_game = -1
        self.seeds = None
        self.histories = []

    def init_game(self):
        '''Initialize players and state.

        Returns:
            dict: first state in one game
            int: current player's id
        '''
        # initialize public variables
        self.current_game += 1
        self.game_result = {0: 0, 1: 0, 2: 0}
        self.histories = []
        self.trace = []
        self.cards_played = []
        self.state = {'deck': None, 'cards_seen': None, 'landlord': None,
                      'self': None, 'hand': None, 'trace': self.trace,
                      'cards_played': None, 'cards_others': None,
                      'remaining': None, 'actions': []}

        # initialize players
        self.players = [Player(num)
                        for num in range(DoudizhuGame.players_num)]

        # initialize round to deal cards and determine landlord
        self.rounder = Round()
        self.rounder.initiate(self.players)
        self.current_player = self.rounder.landlord_num

        # initialize Judger
        self.judger = Judger(self.players)

        # initialize state of landlord to be ready for proceeding round
        player = self.players[self.current_player]
        self.rounder.round_last = get_upstream_player_id(player, self.players)
        deck = init_54_deck()
        deck.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        self.state['deck'] = cards2str(deck)
        self.state['landlord'] = self.rounder.landlord_num
        self.state['self'] = self.current_player
        self.state['hand'] = cards2str(player.hand)
        self.state['cards_seen'] = self.rounder.cards_seen
        self.state['remaining'] = cards2str(player.remaining_cards)
        self.state['cards_others'] = self._get_others_remaining(player)
        self.state['actions'] = list(
            self.judger.playable_cards[self.current_player])
        return copy.deepcopy(self.state), self.current_player

    def step(self, action):
        '''Perform one draw of the game

        Args:
            action (str): specific action of doudizhu. Eg: '33344'

        Returns:
            dict: next player's state
            int: next player's id
        '''
        # record game history
        player = self.players[self.current_player]
        self._record_history()
        self.trace.append((self.current_player, action))

        # update cards played
        if action != 'pass':
            self._add_cards_played(action)
            self.state['cards_played'] = self.cards_played
        # perform action
        greater_player = self.rounder.proceed_round(player, action)
        next_player_id = get_downstream_player_id(player, self.players)

        # update next_state
        self.state['self'] = next_player_id
        next_player = self.players[next_player_id]
        self.state['hand'] = cards2str(next_player.hand)
        self.state['remaining'] = cards2str(next_player.remaining_cards)
        actions = next_player.available_actions(greater_player, self.judger)
        self.state['actions'] = actions
        self.state['cards_others'] = self._get_others_remaining(next_player)
        self.current_player = next_player_id
        return copy.deepcopy(self.state), next_player_id

    def step_back(self):
        '''Return to the previous state of the game.
        '''
        records = self.histories.pop()
        action = self.trace.pop()
        self.current_player = action[0]
        self.rounder.round_last = records['round_last']
        self.cards_played = records['cards_played']
        self.players[self.current_player] = records['player']
        if records['greater_id'] is None:
            self.rounder.greater_player = None
        else:
            self.rounder.greater_player = self.players[records['greater_id']]
        self.judger.playable_cards[self.current_player] = records['plable_cards']

    def get_state(self, player_id):
        '''Return player's state

        Args:
            player_id (int): the player_id of a player

        Returns:
            dict: corresponding player's state
        '''
        player = self.players[player_id]
        if self.current_player is not None:  # when get first state
            return copy.deepcopy(self.state)
        else:  # when get final states of all players
            self.state['self'] = player_id
            self.state['hand'] = cards2str(player.hand)
            self.state['remaining'] = cards2str(player.remaining_cards)
            self.state['actions'] = None
            self.state['cards_others'] = self._get_others_remaining(player)
            return copy.deepcopy(self.state)

    def get_action_num(self):
        '''Return the total number of abstract acitons

        Returns:
            int: the total number of abstract actions of doudizhu
        '''
        return 309

    def get_player_id(self):
        '''Return current player's id

        Returns:
            int: current player's id
        '''
        return self.current_player

    def get_player_num(self):
        '''Return the number of players in doudizhu

        Returns:
            int: the number of players in doudizhu
        '''
        return DoudizhuGame.players_num

    def is_winner(self, player_id):
        '''Judge whether a player is winner in one game

        Args:
            player_id (int): the player_id of a player

        Returns:
            int: 1(winner) / 0(not winner)

        Note:
            1. This function only can be called after game over
        '''
        return self.game_result[player_id]

    def is_over(self):
        '''Judge whether a game is over

        Returns:
            Bool: True(over) / False(not over)
        '''
        if self.current_player is None:
            return True
        last_player = get_upstream_player_id(
            self.players[self.current_player], self.players)
        if len(self.players[last_player].remaining_cards) == 0:
            if self.players[last_player].role == 'peasant':
                for _, player in enumerate(self.players):
                    if player.role == 'peasant':
                        self.game_result[_] = 1
            else:
                self.game_result[last_player] = 1
            self.current_player = None
            return True
        return False

    def _record_history(self):
        '''Record game histories
        '''
        player = self.players[self.current_player]
        records = {'round_last': self.rounder.round_last,
                   'cards_played': self.cards_played.copy(),
                   'plable_cards': self.judger.playable_cards[self.current_player].copy(),
                   'player': copy.deepcopy(player)}
        if self.rounder.greater_player is None:
            records['greater_id'] = None
        else:
            records['greater_id'] = self.rounder.greater_player.player_id
        self.histories.append(records)

    def _get_others_remaining(self, player):
        player_up = self.players[get_upstream_player_id(player, self.players)]
        player_down = self.players[get_downstream_player_id(
            player, self.players)]
        cards_others = (player_up.remaining_cards +
                        player_down.remaining_cards)
        cards_others.sort(key=functools.cmp_to_key(doudizhu_sort_card))
        return cards2str(cards_others)

    def _add_cards_played(self, action):
        self.cards_played.extend(list(action))
        self.cards_played.sort(key=functools.cmp_to_key(doudizhu_sort_str))
