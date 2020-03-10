import numpy as np

from rlcard.envs.env import Env
from rlcard.games.simpledoudizhu.game import SimpleDoudizhuGame as Game
from rlcard.games.doudizhu.utils import SPECIFIC_MAP, CARD_RANK_STR
from rlcard.games.simpledoudizhu.utils import ACTION_LIST, ACTION_SPACE
from rlcard.games.doudizhu.utils import encode_cards


class SimpleDoudizhuEnv(Env):
    ''' SimpleDoudizhu Environment
    '''

    def __init__(self, config):
        self.game = Game()
        super().__init__(config)
        self.state_shape = [6, 5, 15]

    def _extract_state(self, state):
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
        obs = np.zeros((6, 5, 15), dtype=int)
        for index in range(6):
            obs[index][0] = np.ones(15, dtype=int)
        encode_cards(obs[0], state['current_hand'])
        encode_cards(obs[1], state['others_hand'])
        for i, action in enumerate(state['trace'][-3:]):
            if action[1] != 'pass':
                encode_cards(obs[4-i], action[1])
        if state['played_cards'] is not None:
            encode_cards(obs[5], state['played_cards'])

        extrated_state = {'obs': obs, 'legal_actions': self._get_legal_actions()}
        if self.allow_raw_data:
            extracted_state_state['raw_obs'] = state
            extracted_state['raw_legal_actions'] = [a for a in state['actions']]
        if self.record_action:
            extracted_state['action_record'] = self.action_recorder
        return extrated_state

    def get_payoffs(self):
        ''' Get the payoffs of players. Must be implemented in the child class.

        Returns:
            payoffs (list): a list of payoffs for each player
        '''
        return self.game.judger.judge_payoffs(self.game.round.landlord_id, self.game.winner_id)

    def _decode_action(self, action_id):
        ''' Action id -> the action in the game. Must be implemented in the child class.

        Args:
            action_id (int): the id of the action

        Returns:
            action (string): the action that will be passed to the game engine.
        '''
        abstract_action = ACTION_LIST[action_id]
        # without kicker
        if '*' not in abstract_action:
            return abstract_action
        # with kicker
        legal_actions = self.game.state['actions']
        specific_actions = []
        kickers = []
        for legal_action in legal_actions:
            for abstract in SPECIFIC_MAP[legal_action]:
                main = abstract.strip('*')
                if abstract == abstract_action:
                    specific_actions.append(legal_action)
                    kickers.append(legal_action.replace(main, '', 1))
                    break
        # choose kicker with minimum score
        player_id = self.game.get_player_id()
        kicker_scores = []
        for kicker in kickers:
            score = 0
            for action in self.game.judger.playable_cards[player_id]:
                if kicker in action:
                    score += 1
            kicker_scores.append(score+CARD_RANK_STR.index(kicker[0]))
        min_index = 0
        min_score = kicker_scores[0]
        for index, score in enumerate(kicker_scores):
            if score < min_score:
                min_score = score
                min_index = index
        return specific_actions[min_index]

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_action_id = []
        legal_actions = self.game.state['actions']
        if legal_actions:
            for action in legal_actions:
                for abstract in SPECIFIC_MAP[action]:
                    action_id = ACTION_SPACE[abstract]
                    if action_id not in legal_action_id:
                        legal_action_id.append(action_id)
        return legal_action_id

'''
if __name__ == '__main__':
    from rlcard.agents.random_agent import RandomAgent
    env = SimpleDoudizhuEnv()
    env.set_agents([RandomAgent(131), RandomAgent(131), RandomAgent(131)])
    trajectories, payoffs = env.run(is_training=False)
    print(trajectories[0])
'''
