import numpy as np

from rlcard.utils.utils import *
from rlcard.envs.env import Env
from rlcard.games.mahjong.game import MahjongGame as Game
from rlcard.games.mahjong.card import MahjongCard as Card
from rlcard.games.mahjong.utils import *

class MahjongEnv(Env):
    ''' Mahjong Environment
    '''

    def __init__(self, allow_step_back=False):
        super().__init__(Game(allow_step_back), allow_step_back)
        self.action_id = card_encoding_dict
        self.de_action_id = {self.action_id[key]: key for key in self.action_id.keys()}
        self.state_shape = [6, 34, 4]

    def extract_state(self, state):
        ''' Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 6*5*15 array
                         6 : current hand
                             the union of the other two players' hand
                             the recent three actions
                             the union of all played cards
        '''
        players_pile = state['players_pile']
        hand_rep = encode_cards(state['current_hand'])
        piles_rep = []
        for p in players_pile.keys():
            piles_rep.append(encode_cards(pile2list(players_pile[p])))
        piles_rep = np.array(piles_rep)
        table_rep = encode_cards(state['table'])
        rep = [hand_rep, table_rep]
        rep.extend(piles_rep)
        obs = np.array(rep)

        extrated_state = {'obs': obs, 'legal_actions': self.get_legal_actions()}
        return extrated_state

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        _, player, _ = self.game.judger.judge_game(self.game)
        if player == -1:
            payoffs = [0, 0, 0, 0]
        else:
            payoffs = [-1, -1, -1, -1]
            payoffs[player] = 1
        return payoffs

    def decode_action(self, action_id):
        ''' Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (string): the action that will be passed to the game engine.
        '''
        action = self.de_action_id[action_id]
        if action_id < 34:
            candidates = self.game.get_legal_actions(self.game.get_state(self.game.round.current_player))
            for card in candidates:
                if card.get_str() == action:
                    action = card
                    break
        return action

    def get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
        if type(legal_actions[0]) == Card:
            print("GET:", [c.get_str() for c in legal_actions])
        else:
            print(legal_actions)
            legal_actions (list): a list of legal actions' id
        '''
        legal_action_id = []
        legal_actions = self.game.get_legal_actions(self.game.get_state(self.game.round.current_player))
        if legal_actions:
            for action in legal_actions:
                if isinstance(action, Card):
                    action = action.get_str()
                action_id = self.action_id[action]
                legal_action_id.append(action_id)
        else:
            print("##########################")
            print("No Legal Actions")
            print(self.game.judger.judge_game(self.game))
            print(self.game.is_over())
            print([len(p.pile) for p in self.game.players])
            #print(self.game.get_state(self.game.round.current_player))
            #exit()
        return legal_action_id
