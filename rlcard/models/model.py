
class Model(object):
    ''' The base model class
    '''

    def __init__(self):
        ''' Load the model here
        '''
        pass

    @property
    def agents(self):
        ''' Get a list of agents for each position in a the game

        Returns:
            agents (list): A list of agents

        Note: Each agent should be just like RL agent with step and eval_step
              functioning well.
        '''
        raise NotImplementedError
