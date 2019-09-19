from rlcard.envs.env import Env
from rlcard.games.limitholdem.game import LimitholdemGame as Game
from rlcard.utils.utils import *

class LimitholdemEnv(Env):
    ''' Limitholdem Environment
    '''

    def __init__(self):
        ''' Initialize the Limitholdem environment
        '''

        super().__init__(Game())
        self.actions = ['call', 'raise', 'fold', 'check']

    def get_legal_actions(self):
        ''' Get all leagal actions

        Returns:
            encoded_action_list (list): return encoded legal action list (from str to int)
        '''

        return self.game.get_legal_actions()

    def extract_state(self, state):
        ''' Extract the state representation from state dictionary for agent

        Note: Currently the use the hand cards and the public cards. TODO: encode the states

        Args:
            state (dict): Original state from the game

        Returns:
            observation (list): combine the player's score and dealer's observable score for observation
        '''

        return state

    def get_payoffs(self):
        ''' Get the payoff of a game

        Returns:
           payoffs (list): list of payoffs
        '''

        return self.game.get_payoffs()

    def decode_action(self, action_id):
        ''' Decode the action for applying to the game

        Args:
            action id (int): action id

        Returns:
            action (str): action for the game
        '''
        legal_actions = self.game.get_legal_actions()
        if self.actions[action_id] not in legal_actions:
            if 'check' in legal_actions:
                return 'check'
            else:
                return 'fold'

        return self.actions[action_id]
