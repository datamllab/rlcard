import random
import numpy as np

from rlcard.envs.env import Env
from rlcard.games.uno.game import UnoGame as Game
from rlcard.games.uno.utils import encode_hand, encode_target
from rlcard.games.uno.utils import ACTION_SPACE, ACTION_LIST


class UnoEnv(Env):

    def __init__(self):
        super().__init__(Game())

    def extract_state(self, state):
        encoded_state = np.zeros((7, 4, 15), dtype=int)
        encode_hand(encoded_state[:3], state['hand'])
        encode_target(encoded_state[3], state['target'])
        encode_hand(encoded_state[4:], state['others_hand'])
        return encoded_state

    def get_payoffs(self):

        return self.game.get_payoffs()

    def decode_action(self, action_id):
        legal_ids = self.get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        return ACTION_LIST[random.choice(legal_ids)]

    def get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = [ACTION_SPACE[action] for action in legal_actions]
        if not legal_ids:
            legal_ids.append(ACTION_SPACE['draw'])
        return legal_ids
