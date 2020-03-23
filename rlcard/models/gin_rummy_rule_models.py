'''
    File name: models/gin_rummy_rule_models.py
    Author: William Hale
    Date created: 2/12/2020

    Gin Rummy rule models
'''

import numpy as np
import itertools

import rlcard

from rlcard.models.model import Model

from rlcard.games.gin_rummy.utils.action_event import *

import rlcard.games.gin_rummy.utils.melding as melding
import rlcard.games.gin_rummy.utils.utils as utils


class GinRummyNoviceRuleAgent(object):
    '''
        Agent always discards highest deadwood value card
    '''

    def __init__(self):
        self.use_raw = False  # FIXME: should this be True ?

    @staticmethod
    def step(state):
        ''' Predict the action given the current state.
            Novice strategy:
                Case where can gin:
                    Choose one of the gin actions.
                Case where can knock:
                    Choose one of the knock actions.
                Case where can discard:
                    Gin if can. Knock if can.
                    Otherwise, put aside cards in some best meld cluster.
                    Choose one of the remaining cards with highest deadwood value.
                    Discard that card.
                Case otherwise:
                    Choose a random action.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted
        '''
        legal_actions = state['legal_actions']
        actions = legal_actions.copy()
        legal_action_events = [ActionEvent.decode_action(x) for x in legal_actions]
        gin_action_events = [x for x in legal_action_events if isinstance(x, GinAction)]
        knock_action_events = [x for x in legal_action_events if isinstance(x, KnockAction)]
        discard_action_events = [x for x in legal_action_events if isinstance(x, DiscardAction)]
        if gin_action_events:
            actions = [x.action_id for x in gin_action_events]
        elif knock_action_events:
            actions = [x.action_id for x in knock_action_events]
        elif discard_action_events:
            discards = [x.card for x in discard_action_events]  # Note: any card in hand can be discarded
            best_meld_clusters = melding.get_best_meld_clusters(hand=discards, has_extra_card=True)
            best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
            best_meld_cards = list(itertools.chain(*best_meld_cluster))
            candidate_discards = [x for x in discards if x not in best_meld_cards]
            max_deadwood_value = max([utils.get_deadwood_value(card) for card in candidate_discards])
            best_discards = [x for x in candidate_discards if utils.get_deadwood_value(x) == max_deadwood_value]
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


class GinRummyNoviceRuleModel(Model):
    ''' Gin Rummy Rule Model
    '''

    def __init__(self):
        ''' Load pre-trained model
        '''
        super().__init__()
        env = rlcard.make('gin-rummy')
        rule_agent = GinRummyNoviceRuleAgent()
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
