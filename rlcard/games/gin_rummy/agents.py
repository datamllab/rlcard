'''
    File name: gin_rummy/agents.py
    Author: William Hale
    Date created: 2/12/2020
'''

import numpy as np

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.card import Card

import rlcard.games.gin_rummy.utils.utils as utils

#
#   You can choose a random agent or one of the agents below for the opponent of the agent being trained.
#


class HighLowAgent(object):
    ''' Agent always discards highest deadwood value card
    '''

    def __init__(self, action_num):
        ''' Initilize the agent

        Args:
            action_num (int): the size of the output action space
        '''
        self.action_num = action_num

    @staticmethod
    def step(state):
        ''' Predict the action given the current state in training data.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (a card with maximum deadwood value)
        '''
        discard_action_range = range(discard_action_id, discard_action_id + 52)  # 200218 wch kludge
        legal_actions = state['legal_actions']
        actions = legal_actions.copy()
        discard_actions = [action_id for action_id in actions if action_id in discard_action_range]
        if discard_actions:
            discards = [Card.from_card_id(card_id=action_id - discard_action_id) for action_id in discard_actions]
            max_deadwood_value = max([utils.get_deadwood_value(card) for card in discards])
            best_discards = [card for card in discards if utils.get_deadwood_value(card) == max_deadwood_value]
            if best_discards:
                actions = [DiscardAction(card=card).action_id for card in best_discards]
        return np.random.choice(actions)

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the agents is not trained, this function is equivalent to step function.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted by the agent
        '''
        return self.step(state)
