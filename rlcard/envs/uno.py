import numpy as np

from rlcard.envs.env import Env
from rlcard import models
from rlcard.games.uno.game import UnoGame as Game
from rlcard.games.uno.utils import encode_hand, encode_target
from rlcard.games.uno.utils import ACTION_SPACE, ACTION_LIST

class UnoEnv(Env):

    def __init__(self, config):
        self.game = Game()
        super().__init__(config)
        self.state_shape = [7, 4, 15]

    def _load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        return models.load('uno-rule-v1')

    def _extract_state(self, state):
        obs = np.zeros((7, 4, 15), dtype=int)
        encode_hand(obs[:3], state['hand'])
        encode_target(obs[3], state['target'])
        encode_hand(obs[4:], state['others_hand'])
        legal_action_id = self._get_legal_actions()
        extracted_state = {'obs': obs, 'legal_actions': legal_action_id}
        if self.allow_raw_data:
            extracted_state['raw_obs'] = state
            extracted_state['raw_legal_actions'] = [a for a in state['legal_actions']]
        if self.record_action:
            extracted_state['action_record'] = self.action_recorder
        return extracted_state

    def get_payoffs(self):

        return self.game.get_payoffs()

    def _decode_action(self, action_id):
        legal_ids = self._get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        #if (len(self.game.dealer.deck) + len(self.game.round.played_cards)) > 17:
        #    return ACTION_LIST[60]
        return ACTION_LIST[np.random.choice(legal_ids)]

    def _get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = [ACTION_SPACE[action] for action in legal_actions]
        return legal_ids
