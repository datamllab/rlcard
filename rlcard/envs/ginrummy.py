'''
    File name: envs/gin_rummy.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard import models

from rlcard.envs.env import Env
from rlcard.games.gin_rummy.action_event import *
from rlcard.games.gin_rummy.game import GinRummyGame as Game
from rlcard.games.gin_rummy.judge import GinRummyJudge
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.scorers import Scorer

import numpy as np
import rlcard.games.gin_rummy.scorers as scorers
import rlcard.games.gin_rummy.utils as utils

from typing import Callable


class GinRummyEnv(Env):
    ''' GinRummy Environment
    '''

    def __init__(self, allow_step_back=False, allow_raw_data=False):
        super().__init__(Game(allow_step_back), allow_step_back, allow_raw_data)
        self.state_shape = [5, 52]
        self.judge = GinRummyJudge(game=self.game)
        self.scorer: Scorer = scorers.GinRummyScorer()

    def extract_state(self, state):  # 200213 don't use state ???
        ''' Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 5 * 52 array
                         5 : current hand (1 if card in hand else 0)
                             top_discard (1 if card is top discard else 0)
                             dead_cards (1 for discards except for top_discard else 0)
                             opponent known cards (likewise)
                             unknown cards (likewise)  # is this needed ??? 200213
        '''
        if self.game.is_over():
            obs = np.array([utils.encode_cards([]) for _ in range(5)])
            extracted_state = {'obs': obs, 'legal_actions': self.get_legal_actions()}
        else:
            discard_pile = self.game.round.dealer.discard_pile
            stock_pile = self.game.round.dealer.stock_pile
            top_discard = [] if not discard_pile else [discard_pile[-1]]
            dead_cards = discard_pile[:-1]
            current_player = self.game.get_current_player()
            opponent = self.game.round.players[(current_player.player_id + 1) % 2]
            known_cards = opponent.known_cards
            unknown_cards = stock_pile + [card for card in opponent.hand if card not in known_cards]
            hand_rep = utils.encode_cards(current_player.hand)
            top_discard_rep = utils.encode_cards(top_discard)
            dead_cards_rep = utils.encode_cards(dead_cards)
            known_cards_rep = utils.encode_cards(known_cards)
            unknown_cards_rep = utils.encode_cards(unknown_cards)
            rep = [hand_rep, top_discard_rep, dead_cards_rep, known_cards_rep, unknown_cards_rep]
            obs = np.array(rep)
            extracted_state = {'obs': obs, 'legal_actions': self.get_legal_actions()}
        return extracted_state

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        payoffs = self.scorer.get_payoffs(game=self.game)
        return payoffs

    def decode_action(self, action_id) -> ActionEvent:  # FIXME 200213 should return str
        ''' Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        return self.game.decode_action(action_id=action_id)

    def get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_actions = self.judge.get_legal_actions()
        legal_actions_ids = [action_event.action_id for action_event in legal_actions]
        return legal_actions_ids

    def set_scorer(self, printing_configuration: bool = False,
                   get_payoff: Callable[[GinRummyPlayer, Game], int or float] = None):
        if self.game.settings.scorer_name == "GinRummyScorer":
            self.scorer = scorers.GinRummyScorer(get_payoff=get_payoff)
        elif self.game.settings.scorer_name == "HighLowScorer":
            self.scorer = scorers.HighLowScorer(get_payoff=get_payoff)
        else:
            raise Exception("GinRummyEnv: cannot determine scorer.")
        if printing_configuration:
            print("")
            print("========== Scorer ==========")
            print(f"Scorer is {self.scorer.name}")
            print("============================")

    def print_state(self, player):  # FIXME: stub
        ''' Print out the state of a given player

        Args:
            player (int): Player id
        '''
        state = self.game.get_state(player)  # FIXME: should I be using just this ???
        dealer_id = self.game.round.dealer_id
        current_player_id = self.game.round.current_player_id
        stock_pile = self.game.round.dealer.stock_pile
        discard_pile = self.game.round.dealer.discard_pile
        #  FIXME: game needs card sort function
        north_held_pile = sorted(self.game.round.players[0].hand, key=lambda card: card.card_id, reverse=True)
        south_held_pile = sorted(self.game.round.players[1].hand, key=lambda card: card.card_id, reverse=True)
        print('\n=============== Your Hand ===============')
        print(f"{[str(card) for card in south_held_pile]}")
        print('')
        print('=============== Last Card ===============')
        print('')
        print('========== Agents Card Number ===========')
        for i in range(self.player_num):
            if i != self.active_player:
                print('Agent {} has {} cards.'.format(i, len(self.game.round.players[i].hand)))
        print('======== Actions You Can Choose =========')
        # for i, action in enumerate(state['legal_actions']):
        #     if i < len(state['legal_actions']) - 1:
        #         print(', ', end='')
        print('\n')
        # FIXME: new version
        lines = []
        lines.append(f"--- New version ---")
        #  FIXME: game needs short name for player
        # lines.append(f"dealer: {utils.player_short_name(dealer_id)}")
        # lines.append(f"current_player: {utils.player_short_name(current_player_id)}")
        lines.append(f"dealer: {dealer_id}")
        lines.append(f"current_player: {current_player_id}")
        lines.append(f"north hand: {[str(card) for card in north_held_pile]}")
        lines.append(f"stockpile: {[str(card) for card in stock_pile]}")
        lines.append(f"discard pile: {[str(card) for card in discard_pile]}")
        lines.append(f"south hand: {[str(card) for card in south_held_pile]}")
        print("\n".join(lines))


    def print_result(self, player):
        ''' Print the game result when the game is over

        Args:
            player (int): The human player id
        '''
        print(f"GinRummyEnv print_result: player={player}")  # FIXME: stub

    @staticmethod
    def print_action(action):
        ''' Print out an action in a nice form

        Args:
            action (str): A string a action
        '''
        print(f"GinRummyEnv print_action: action={action}")  # FIXME: stub

    def load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        assert False  # FIXME: stub
        return models.load('uno-rule-v1')  # FIXME: stub
