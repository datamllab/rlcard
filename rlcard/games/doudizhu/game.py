# -*- coding: utf-8 -*-
''' Implement Doudizhu Game class
'''
import functools
from heapq import merge
import numpy as np

from rlcard.games.doudizhu.utils import cards2str, doudizhu_sort_card, CARD_RANK_STR
from rlcard.games.doudizhu import Player
from rlcard.games.doudizhu import Round
from rlcard.games.doudizhu import Judger


class DoudizhuGame:
    ''' Provide game APIs for env to run doudizhu and get corresponding state
    information.
    '''
    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
        self.np_random = np.random.RandomState()
        self.num_players = 3

    def init_game(self):
        ''' Initialize players and state.

        Returns:
            dict: first state in one game
            int: current player's id
        '''
        # initialize public variables
        self.winner_id = None
        self.history = []

        # initialize players
        self.players = [Player(num, self.np_random)
                        for num in range(self.num_players)]

        # initialize round to deal cards and determine landlord
        self.played_cards = [np.zeros((len(CARD_RANK_STR), ), dtype=np.int)
                                for _ in range(self.num_players)]
        self.round = Round(self.np_random, self.played_cards)
        self.round.initiate(self.players)

        # initialize judger
        self.judger = Judger(self.players, self.np_random)

        # get state of first player
        player_id = self.round.current_player
        self.state = self.get_state(player_id)

        return self.state, player_id

    def step(self, action):
        ''' Perform one draw of the game

        Args:
            action (str): specific action of doudizhu. Eg: '33344'

        Returns:
            dict: next player's state
            int: next player's id
        '''
        if self.allow_step_back:
            # TODO: don't record game.round, game.players, game.judger if allow_step_back not set
            pass

        # perfrom action
        player = self.players[self.round.current_player]
        self.round.proceed_round(player, action)
        if (action != 'pass'):
            self.judger.calc_playable_cards(player)
        if self.judger.judge_game(self.players, self.round.current_player):
            self.winner_id = self.round.current_player
        next_id = (player.player_id+1) % len(self.players)
        self.round.current_player = next_id

        # get next state
        state = self.get_state(next_id)
        self.state = state

        return state, next_id

    def step_back(self):
        ''' Return to the previous state of the game

        Returns:
            (bool): True if the game steps back successfully
        '''
        if not self.round.trace:
            return False

        #winner_id will be always None no matter step_back from any case
        self.winner_id = None

        #reverse round
        player_id, cards = self.round.step_back(self.players)

        #reverse player
        if (cards != 'pass'):
            self.players[player_id].played_cards = self.round.find_last_played_cards_in_trace(player_id)
        self.players[player_id].play_back()

        #reverse judger.played_cards if needed
        if (cards != 'pass'):
            self.judger.restore_playable_cards(player_id)

        self.state = self.get_state(self.round.current_player)
        return True

    def get_state(self, player_id):
        ''' Return player's state

        Args:
            player_id (int): player id

        Returns:
            (dict): The state of the player
        '''
        player = self.players[player_id]
        others_hands = self._get_others_current_hand(player)
        num_cards_left = [len(self.players[i].current_hand) for i in range(self.num_players)]
        if self.is_over():
            actions = []
        else:
            actions = list(player.available_actions(self.round.greater_player, self.judger))
        state = player.get_state(self.round.public, others_hands, num_cards_left, actions)

        return state

    @staticmethod
    def get_num_actions():
        ''' Return the total number of abstract acitons

        Returns:
            int: the total number of abstract actions of doudizhu
        '''
        return 27472

    def get_player_id(self):
        ''' Return current player's id

        Returns:
            int: current player's id
        '''
        return self.round.current_player

    def get_num_players(self):
        ''' Return the number of players in doudizhu

        Returns:
            int: the number of players in doudizhu
        '''
        return self.num_players

    def is_over(self):
        ''' Judge whether a game is over

        Returns:
            Bool: True(over) / False(not over)
        '''
        if self.winner_id is None:
            return False
        return True

    def _get_others_current_hand(self, player):
        player_up = self.players[(player.player_id+1) % len(self.players)]
        player_down = self.players[(player.player_id-1) % len(self.players)]
        others_hand = merge(player_up.current_hand, player_down.current_hand, key=functools.cmp_to_key(doudizhu_sort_card))
        return cards2str(others_hand)
