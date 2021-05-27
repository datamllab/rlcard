'''
    Project: Gui Gin Rummy
    File name: gin_rummy_human_agent.py
    Author: William Hale
    Date created: 3/14/2020
'''

import time

from rlcard.games.gin_rummy.utils.action_event import ActionEvent
from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError


class HumanAgent(object):
    ''' A human agent for Gin Rummy. It can be used to play against trained models.
    '''

    def __init__(self, num_actions):
        ''' Initialize the human agent

        Args:
            num_actions (int): the size of the output action space
        '''
        self.use_raw = True
        self.num_actions = num_actions
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
        if self.is_choosing_action_id:
            raise GinRummyProgramError("self.is_choosing_action_id must be False.")
        if self.state is not None:
            raise GinRummyProgramError("self.state must be None.")
        if self.chosen_action_id is not None:
            raise GinRummyProgramError("self.chosen_action_id={} must be None.".format(self.chosen_action_id))
        self.state = state
        self.is_choosing_action_id = True
        while not self.chosen_action_id:
            time.sleep(0.001)
        if self.chosen_action_id is None:
            raise GinRummyProgramError("self.chosen_action_id cannot be None.")
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
        '''
        return self.step(state), {}
