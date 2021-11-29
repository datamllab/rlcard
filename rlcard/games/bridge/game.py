'''
    File name: bridge/game.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

import numpy as np

from .judger import BridgeJudger
from .round import BridgeRound
from .utils.action_event import ActionEvent, CallActionEvent, PlayCardAction


class BridgeGame:
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, allow_step_back=False):
        '''Initialize the class BridgeGame
        '''
        self.allow_step_back: bool = allow_step_back
        self.np_random = np.random.RandomState()
        self.judger: BridgeJudger = BridgeJudger(game=self)
        self.actions: [ActionEvent] = []  # must reset in init_game
        self.round: BridgeRound or None = None  # must reset in init_game
        self.num_players: int = 4

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        board_id = self.np_random.choice([1, 2, 3, 4])
        self.actions: List[ActionEvent] = []
        self.round = BridgeRound(num_players=self.num_players, board_id=board_id, np_random=self.np_random)
        for player_id in range(4):
            player = self.round.players[player_id]
            self.round.dealer.deal_cards(player=player, num=13)
        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def step(self, action: ActionEvent):
        ''' Perform game action and return next player number, and the state for next player
        '''
        if isinstance(action, CallActionEvent):
            self.round.make_call(action=action)
        elif isinstance(action, PlayCardAction):
            self.round.play_card(action=action)
        else:
            raise Exception(f'Unknown step action={action}')
        self.actions.append(action)
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def get_num_players(self) -> int:
        ''' Return the number of players in the game
        '''
        return self.num_players

    @staticmethod
    def get_num_actions() -> int:
        ''' Return the number of possible actions in the game
        '''
        return ActionEvent.get_num_actions()

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        return self.round.current_player_id

    def is_over(self) -> bool:
        ''' Return whether the current game is over
        '''
        return self.round.is_over()

    def get_state(self, player_id: int):  # wch: not really used
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = {}
        if not self.is_over():
            state['player_id'] = player_id
            state['current_player_id'] = self.round.current_player_id
            state['hand'] = self.round.players[player_id].hand
        else:
            state['player_id'] = player_id
            state['current_player_id'] = self.round.current_player_id
            state['hand'] = self.round.players[player_id].hand
        return state
