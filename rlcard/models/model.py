
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

    @property
    def use_raw(self):
        ''' Indicate whether use raw state and action

        Returns:
            use_raw (boolean): True if using raw state and action
        '''
        raise NotImplementedError
