import random
import numpy as np
from rlcard.utils.utils import *
from rlcard.envs.env import Env
from rlcard.games.doudizhu import *
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.games.doudizhu.utils import CARD_RANK_STR, SPECIFIC_MAP
from rlcard.games.doudizhu.utils import ACTION_LIST, ACTION_SPACE
from rlcard.games.doudizhu.utils import encode_cards


class DoudizhuEnv(Env):
    '''
    Doudizhu Environment
    '''

    def __init__(self):
        super().__init__(Game())

    def extract_state(self, state):
        '''Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 6*5*15 array
                         6 : current hand
                             the union of the other two players' hand
                             the recent three actions
                             the union of all played cards
        '''
        encoded_state = np.zeros((6, 5, 15), dtype=int)
        for index in range(6):
            encoded_state[index][0] = np.ones(15, dtype=int)
        encode_cards(encoded_state[0], state['current_hand'])
        encode_cards(encoded_state[1], state['others_hand'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                encode_cards(encoded_state[4-i], action[1])
        if state['played_cards'] is not None:
            encode_cards(encoded_state[5], state['played_cards'])
        return encoded_state

    def get_payoffs(self):
        '''Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        return self.game.game_result

    def decode_action(self, action_id):
        '''Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (string): the action that will be passed to the game engine.
        '''
        abstract_action = ACTION_LIST[action_id]
        legal_actions = self.game.state['actions']
        specific_actions = []
        for legal_action in legal_actions:
            for abstract in SPECIFIC_MAP[legal_action]:
                if abstract == abstract_action:
                    specific_actions.append(legal_action)
        if specific_actions:
            action = random.choice(specific_actions)
        else:
            if "pass" in legal_actions:
                action = "pass"
            else:
                action = random.choice(legal_actions)
        return action

    def get_legal_actions(self):
        '''Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_action_id = []
        legal_actions = self.game.state['actions']
        for action in legal_actions:
            for abstract in SPECIFIC_MAP[action]:
                action_id = ACTION_SPACE[abstract]
                if action_id not in legal_action_id:
                    legal_action_id.append(action_id)
        return legal_action_id
