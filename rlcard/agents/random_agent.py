import random

class RandomAgent(object):
    """ 
        A random agent. Random agents is for running toy examples on the card games
    """

    def __init__(self, action_size):
        """ Initilize the random agent

        Args:
            action_size (int): the size of the ouput action space
        """
        
        self.action_size = action_size
        
    def step(self, state):
        """ Predict the action given the curent state in gerenerating training data.

        Args:
            state (numpy array): an numpy array that represents the current state

        Returns:
            action: the action predicted (randomly chosen) by the random agent
        """
        return random.randint(0, self.action_size-1)

    def eval_step(self, state):
        """ Predict the action given the curent state for evaluation.
            Since the random agents are not trained. This function is equivalent to step function
        """
        return self.step(state)


