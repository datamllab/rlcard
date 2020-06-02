import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from .determism_util import is_deterministic

class TestMahjongEnv(unittest.TestCase):

    def test_reset_and_extract_state(self):
        env = rlcard.make('mahjong')
        state, _ = env.reset()
        self.assertEqual(state['obs'].size, 816)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('mahjong'))

    def test_get_legal_actions(self):
        env = rlcard.make('mahjong')
        env.set_agents([RandomAgent(env.action_num) for _ in range(env.player_num)])
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, env.action_num-1)

    def test_step(self):
        env = rlcard.make('mahjong')
        state, _ = env.reset()
        action = np.random.choice(state['legal_actions'])
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.game.round.current_player)

    def test_step_back(self):
        env = rlcard.make('mahjong', config={'allow_step_back':True})
        state, player_id = env.reset()
        action = np.random.choice(state['legal_actions'])
        env.step(action)
        env.step_back()
        self.assertEqual(env.game.round.current_player, player_id)

        env = rlcard.make('mahjong', config={'allow_step_back':False})
        state, player_id = env.reset()
        action = np.random.choice(state['legal_actions'])
        env.step(action)
        # env.step_back()
        self.assertRaises(Exception, env.step_back)

    def test_run(self):
        env = rlcard.make('mahjong')
        env.set_agents([RandomAgent(env.action_num) for _ in range(env.player_num)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 4)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)
        trajectories, payoffs = env.run(is_training=True)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)

if __name__ == '__main__':
    unittest.main()
