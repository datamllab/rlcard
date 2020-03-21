'''
    File name: models/gin_rummy_rule_models.py
    Author: William Hale
    Date created: 2/12/2020

    Gin Rummy rule models
'''

import numpy as np

import rlcard
from rlcard.models.model import Model

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.card import Card

import rlcard.games.gin_rummy.utils.utils as utils


class GinRummyRuleAgent(object):
    '''
        Agent always discards highest deadwood value card
    '''

    def __init__(self):
        self.use_raw = False  # FIXME: should this be True ?

    @staticmethod
    def step(state):
        ''' Predict the action given the current state.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted
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
            probabilities (list): The list of action probabilities
        '''
        probabilities = []
        return self.step(state), probabilities


class GinRummyRuleModel(Model):
    ''' Gin Rummy Rule Model
    '''

    def __init__(self):
        ''' Load pre-trained model
        '''
        super().__init__()
        env = rlcard.make('gin-rummy')
        rule_agent = GinRummyRuleAgent()
        self.rule_agents = [rule_agent for _ in range(env.player_num)]

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        return self.rule_agents
