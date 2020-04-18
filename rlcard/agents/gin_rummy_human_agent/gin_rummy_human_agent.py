'''
    Project: Gui Gin Rummy
    File name: gin_rummy_human_agent.py
    Author: William Hale
    Date created: 3/14/2020
'''

import time

from rlcard.games.gin_rummy.utils.action_event import ActionEvent


class HumanAgent(object):
    ''' A human agent for Gin Rummy. It can be used to play against trained models.
    '''

    def __init__(self, action_num):
        ''' Initialize the human agent

        Args:
            action_num (int): the size of the output action space
        '''
        self.use_raw = True
        self.action_num = action_num
        self.is_choosing_action_id = False
        self.chosen_action_id = None  # type: int or None
        self.state = None

    def step(self, state):
        ''' Human agent will display the state and make decisions through interfaces

        Args:
            state (dict): A dictionary that represents the current state

        Returns:
            action (int): The action decided by human
        '''
        assert not self.is_choosing_action_id
        assert self.state is None
        assert self.chosen_action_id is None
        self.state = state
        self.is_choosing_action_id = True
        while not self.chosen_action_id:
            time.sleep(0.001)
        assert self.chosen_action_id is not None
        chosen_action_event = ActionEvent.decode_action(action_id=self.chosen_action_id)
        self.state = None
        self.is_choosing_action_id = False
        self.chosen_action_id = None
        return chosen_action_event

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
            probabilities (list): The list of action probabilities
        '''
        return self.step(state), []
