import numpy as np


class RandomAgent(object):
    ''' A random agent. Random agents is for running toy examples on the card games
    '''

    def __init__(self, action_num):
        ''' Initilize the random agent

        Args:
            action_num (int): the size of the ouput action space
        '''

        self.action_num = action_num

    def step(self, state):
        ''' Predict the action given the curent state in gerenerating training data.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''

        #return np.random.randint(0, self.action_num)
        return np.random.choice(state['legal_actions'])

    def eval_step(self, state):
        ''' Predict the action given the curent state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''

        return self.step(state)
