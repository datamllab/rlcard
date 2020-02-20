# -*- coding: utf-8 -*-
''' Implement Doudizhu Game class
'''

import functools
from heapq import merge

from rlcard.games.doudizhu.judger import cards2str
from rlcard.games.doudizhu.player import DoudizhuPlayer as Player
from rlcard.games.doudizhu.round import DoudizhuRound as Round
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger
from rlcard.games.doudizhu.utils import doudizhu_sort_card
from rlcard.utils.utils import get_downstream_player_id, get_upstream_player_id


class DoudizhuGame(object):
    ''' Provide game APIs for env to run doudizhu and get corresponding state
    information.

    An example of state during runtime:
            {
             'deck': '3333444455556666777788889999TTTTJJJJQQQQKKKKAAAA2222BR',
             'seen_cards': 'TQA',
             'landlord': 0,
             'self': 2,
             'initial_hand': '3456677799TJQKAAB',
             'trace': [(0, '8222'), (1, 'pass'), (2, 'pass'), (0, '6KKK'),
                       (1, 'pass'), (2, 'pass'), (0, '8'), (1, 'Q')],
             'played_cards': ['6', '8', '8', 'Q', 'K', 'K', 'K', '2', '2', '2'],
             'others_hand': '333444555678899TTTJJJQQAA2R',
             'current_hand': '3456677799TJQKAAB',
             'actions': ['pass', 'K', 'A', 'B']
            }
    '''

    def __init__(self, allow_step_back=False):
        self.allow_step_back = allow_step_back
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
        self.players = [Player(num)
                        for num in range(self.num_players)]

        # initialize round to deal cards and determine landlord
        self.round = Round()
        self.round.initiate(self.players)

        # initialize judger
        self.judger = Judger(self.players)

        # get state of first player
        player_id = self.round.current_player
        player = self.players[player_id]
        others_hands = self._get_others_current_hand(player)
        actions = list(self.judger.playable_cards[player_id])
        state = player.get_state(self.round.public, others_hands, actions)
        self.state = state

        return state, player_id

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
        next_id = get_downstream_player_id(player, self.players)
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
        if self.is_over():
            actions = None
        else:
            actions = list(player.available_actions(self.round.greater_player, self.judger))
        state = player.get_state(self.round.public, others_hands, actions)

        return state

    @staticmethod
    def get_action_num():
        ''' Return the total number of abstract acitons

        Returns:
            int: the total number of abstract actions of doudizhu
        '''
        return 309

    def get_player_id(self):
        ''' Return current player's id

        Returns:
            int: current player's id
        '''
        return self.round.current_player

    def get_player_num(self):
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
        player_up = self.players[get_upstream_player_id(player, self.players)]
        player_down = self.players[get_downstream_player_id(
            player, self.players)]
        others_hand = merge(player_up.current_hand, player_down.current_hand, key=functools.cmp_to_key(doudizhu_sort_card))
        return cards2str(others_hand)

#if __name__ == '__main__':

    # test init game
    #game = DoudizhuGame()
    #game.init_game()
