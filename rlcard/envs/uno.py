import numpy as np

from rlcard.envs.env import Env
from rlcard import models
from rlcard.games.uno.game import UnoGame as Game
from rlcard.games.uno.utils import encode_hand, encode_target
from rlcard.games.uno.utils import ACTION_SPACE, ACTION_LIST
from rlcard.games.uno.card import UnoCard


class UnoEnv(Env):

    def __init__(self, allow_step_back=False):
        super().__init__(Game(allow_step_back), allow_step_back)
        self.state_shape = [7, 4, 15]

    def print_state(self, player):
        ''' Print out the state of a given player

        Args:
            player (int): Player id
        '''
        state = self.game.get_state(player)
        print('\n=============== Your Hand ===============')
        UnoCard.print_cards(state['hand'])
        print('')
        print('=============== Last Card ===============')
        UnoCard.print_cards(state['target'], wild_color=True)
        print('')
        print('========== Agents Card Number ===========')
        for i in range(self.player_num):
            if i != self.active_player:
                print('Agent {} has {} cards.'.format(i, len(self.game.players[i].hand)))
        print('======== Actions You Can Choose =========')
        for i, action in enumerate(state['legal_actions']):
            print(str(ACTION_SPACE[action])+': ', end='')
            UnoCard.print_cards(action, wild_color=True)
            if i < len(state['legal_actions']) - 1:
                print(', ', end='')
        print('\n')

    def print_result(self, player):
        ''' Print the game result when the game is over

        Args:
            player (int): The human player id
        '''
        payoffs = self.get_payoffs()
        print('===============     Result     ===============')
        if payoffs[player] > 0:
            print('You win!')
        else:
            print('You lose!')
        print('')

    @staticmethod
    def print_action(action):
        ''' Print out an action in a nice form

        Args:
            action (str): A string a action
        '''
        UnoCard.print_cards(action, wild_color=True)

    def load_model(self):
        ''' Load pretrained/rule model

        Returns:
            model (Model): A Model object
        '''
        return models.load('uno-rule-v1')

    def extract_state(self, state):
        obs = np.zeros((7, 4, 15), dtype=int)
        encode_hand(obs[:3], state['hand'])
        encode_target(obs[3], state['target'])
        encode_hand(obs[4:], state['others_hand'])
        legal_action_id = self.get_legal_actions()
        extrated_state = {'obs': obs, 'legal_actions': legal_action_id}
        return extrated_state

    def get_payoffs(self):

        return self.game.get_payoffs()

    def decode_action(self, action_id):
        legal_ids = self.get_legal_actions()
        if action_id in legal_ids:
            return ACTION_LIST[action_id]
        #if (len(self.game.dealer.deck) + len(self.game.round.played_cards)) > 17:
        #    return ACTION_LIST[60]
        return ACTION_LIST[np.random.choice(legal_ids)]

    def get_legal_actions(self):
        legal_actions = self.game.get_legal_actions()
        legal_ids = [ACTION_SPACE[action] for action in legal_actions]
        return legal_ids
