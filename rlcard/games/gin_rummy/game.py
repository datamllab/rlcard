'''
    File name: gin_rummy/game.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List

import random

from rlcard.core import Game

from .player import GinRummyPlayer
from .round import GinRummyRound
from .judge import GinRummyJudge
from .utils.settings import Settings, DealerForRound

from .utils.action_event import *


class GinRummyGame(Game):
    ''' Game class. This class will interact with outer environment.
    '''

    def __init__(self, allow_step_back=False):
        '''Initialize the class GinRummyGame
        '''
        self.allow_step_back = allow_step_back
        self.judge = GinRummyJudge(game=self)
        self.settings = Settings()
        self.actions = None  # type: List[ActionEvent] or None # must reset in init_game
        self.round = None  # round: GinRummyRound or None, must reset in init_game

    def init_game(self):
        ''' Initialize all characters in the game and start round 1
        '''
        dealer_id = random.choice([0, 1])
        if self.settings.dealer_for_round == DealerForRound.North:
            dealer_id = 0
        elif self.settings.dealer_for_round == DealerForRound.South:
            dealer_id = 1
        self.actions = []
        self.round = GinRummyRound(dealer_id=dealer_id)
        for i in range(2):
            num = 11 if i == 0 else 10
            player = self.round.players[(dealer_id + 1 + i) % 2]
            self.round.dealer.deal_cards(player=player, num=num)
        current_player_id = self.round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def step(self, action: ActionEvent):
        ''' Perform game action and return next player number, and the state for next player
        '''
        if type(action) is ScoreNorthPlayerAction:
            self.round.score_player_0(action)
        elif type(action) is ScoreSouthPlayerAction:
            self.round.score_player_1(action)
        elif type(action) is DrawCardAction:
            self.round.draw_card(action)
        elif type(action) is PickUpDiscardAction:
            self.round.pick_up_discard(action)
        elif type(action) is DeclareDeadHandAction:
            self.round.declare_dead_hand(action)
        elif type(action) is GinAction:
            self.round.gin(action)
        elif type(action) is DiscardAction:
            self.round.discard(action)
        elif type(action) is KnockAction:
            self.round.knock(action)
        else:
            raise Exception('Unknown step action={}'.format(action))
        self.actions.append(action)
        next_player_id = self.round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def step_back(self):
        ''' Takes one step backward and restore to the last state
        '''
        raise NotImplementedError

    def get_player_num(self):
        ''' Return the number of players in the game
        '''
        return 2

    def get_action_num(self):
        ''' Return the number of possible actions in the game
        '''
        return ActionEvent.get_action_num()

    def get_player_id(self):
        ''' Return the current player that will take actions soon
        '''
        return self.round.current_player_id

    def is_over(self):
        ''' Return whether the current game is over
        '''
        return self.round.is_over

    def get_current_player(self) -> GinRummyPlayer or None:
        return self.round.get_current_player()

    def get_last_action(self) -> ActionEvent or None:
        return None if len(self.actions) == 0 else self.actions[-1]

    def get_state(self, player_id: int):
        ''' Get player's state

        Return:
            state (dict): The information of the state
        '''
        state = {}
        if not self.is_over():
            discard_pile = self.round.dealer.discard_pile
            top_discard = [] if not discard_pile else [discard_pile[-1]]
            dead_cards = discard_pile[:-1]
            last_action = self.get_last_action()
            opponent_id = (player_id + 1) % 2
            opponent = self.round.players[opponent_id]
            known_cards = opponent.known_cards
            if type(last_action) is ScoreNorthPlayerAction or type(last_action) is ScoreSouthPlayerAction:
                known_cards = opponent.hand
            unknown_cards = self.round.dealer.stock_pile + [card for card in opponent.hand if card not in known_cards]
            state['player_id'] = self.round.current_player_id
            state['hand'] = [x.get_index() for x in self.round.players[self.round.current_player_id].hand]
            state['top_discard'] = [x.get_index() for x in top_discard]
            state['dead_cards'] = [x.get_index() for x in dead_cards]
            state['opponent_known_cards'] = [x.get_index() for x in known_cards]
            state['unknown_cards'] = [x.get_index() for x in unknown_cards]
        return state

    @staticmethod
    def decode_action(action_id) -> ActionEvent:  # FIXME 200213 should return str
        ''' Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        return ActionEvent.decode_action(action_id=action_id)
