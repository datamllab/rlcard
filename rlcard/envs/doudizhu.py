import random
import numpy as np
from rlcard.utils.utils import *
from rlcard.envs.env import Env
from rlcard.games.doudizhu import *
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.games.doudizhu.utils import CARD_RANK_STR, SPECIFIC_MAP, ACTION_LIST
from rlcard.games.doudizhu.utils import encode_cards


class DoudizhuEnv(Env):
    """
    Doudizhu Environment
    """

    def __init__(self):
        super().__init__(Game())

    def extract_state(self, state):
        """Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 6*5*15 array
                         6 : current player's cards
                             union other players' cards
                             recent three actions
                             union of played cards
        """
        encoded_state = np.zeros((6, 5, 15), dtype=int)
        encode_cards(encoded_state[0], state['remaining'])
        encode_cards(encoded_state[1], state['cards_others'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                encode_cards(encoded_state[4-i], action[1])
        if state['cards_played'] is not None:
            encode_cards(encoded_state[5], state['cards_played'])
        return encoded_state

    def get_payoffs(self):
        return self.game.game_result

    def decode_action(self, action_id):
        abstract_action = ACTION_LIST[action_id]
        legal_actions = self.game.state['actions']
        specific_actions = []
        for legal_action in legal_actions:
            for abstract in SPECIFIC_MAP[legal_action]:
                if abstract == abstract_action:
                    specific_actions.append(legal_action)
        if specific_actions:
            return random.choice(specific_actions)
        return random.choice(legal_actions)
