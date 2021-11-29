'''
    File name: models/bridge_rule_models.py
    Author: William Hale
    Date created: 11/27/2021

    Bridge rule models
'''

import numpy as np

from rlcard.games.bridge.utils.action_event import ActionEvent


class BridgeDefenderNoviceRuleAgent(object):
    '''
        Agent always passes during bidding
    '''

    def __init__(self):
        self.use_raw = False

    @staticmethod
    def step(state) -> int:
        ''' Predict the action given the current state.
            Defender Novice strategy:
                Case during make call:
                    Always choose PassAction.
                Case during play card:
                    Choose a random action.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action_id (int): the action_id predicted
        '''
        legal_action_ids = state['raw_legal_actions']
        if ActionEvent.pass_action_id in legal_action_ids:
            selected_action_id = ActionEvent.pass_action_id
        else:
            selected_action_id = np.random.choice(legal_action_ids)
        return selected_action_id

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation.
            Since the agents is not trained, this function is equivalent to step function.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action_id (int): the action_id predicted by the agent
            probabilities (list): The list of action probabilities
        '''
        probabilities = []
        return self.step(state), probabilities
