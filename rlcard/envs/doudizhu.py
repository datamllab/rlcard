import random
import numpy as np
from rlcard.envs.env import Env
from rlcard.games.doudizhu import *
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.games.doudizhu.utils import CARD_RANK_STR, SPECIFIC_MAP, ACTION_LIST


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
            numpy array: 6×60 array
                         60: 4 suits cards of 15 ranks from 3 to red joker
                         6 : current player's cards
                             union other players' cards
                             recent three actions
                             union of played cards
        """

        def add_cards(array, cards):
            suit = 0
            for index, card in enumerate(cards):
                if index != 0 and card == cards[index-1]:
                    suit += 1
                else:
                    suit = 0
                rank = CARD_RANK_STR.index(card)
                array[rank+suit*15] += 1

        encoded_state = np.zeros((6, 60), dtype=int)
        add_cards(encoded_state[0], state['remaining'])
        add_cards(encoded_state[1], state['cards_others'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                add_cards(encoded_state[4-i], action[1])
        if state['cards_played'] is not None:
            add_cards(encoded_state[5], state['cards_played'])
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
        if len(specific_actions) > 0:
            return random.choice(specific_actions)
        return random.choice(legal_actions)
