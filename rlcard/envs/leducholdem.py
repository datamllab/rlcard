import json
import os
import numpy as np

import rlcard
from rlcard.envs.env import Env
from rlcard.games.leducholdem.game import LeducholdemGame as Game
from rlcard.utils.utils import *

class LeducholdemEnv(Env):
    ''' Limitholdem Environment
    '''

    def __init__(self, allow_step_back=False):
        ''' Initialize the Limitholdem environment
        '''

        super().__init__(Game(allow_step_back), allow_step_back)
        self.actions = ['call', 'raise', 'fold', 'check']

        with open(os.path.join(rlcard.__path__[0], 'games/leducholdem/card2index.json'), 'r') as file:
            self.card2index = json.load(file)

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

        processed_state = {}

        legal_actions = [self.actions.index(a) for a in state['legal_actions']]
        processed_state['legal_actions'] = legal_actions

        public_card = state['public_card']
        hand = state['hand']
        cards = [] + [hand]
        if public_card:
            cards.append(public_card)
        idx = [self.card2index[card] for card in cards]
        obs = np.zeros(6)
        obs[idx] = 1
        processed_state['obs'] = obs

        return processed_state

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
