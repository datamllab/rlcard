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
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, env.num_actions-1)

    def test_step(self):
        env = rlcard.make('mahjong')
        state, _ = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.game.round.current_player)

    def test_step_back(self):
        env = rlcard.make('mahjong', config={'allow_step_back':True})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        env.step_back()
        self.assertEqual(env.game.round.current_player, player_id)

        env = rlcard.make('mahjong', config={'allow_step_back':False})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        # env.step_back()
        self.assertRaises(Exception, env.step_back)

    def test_run(self):
        env = rlcard.make('mahjong')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        trajectories, payoffs = env.run(is_training=False)
        trajectories, payoffs = env.run(is_training=True)

if __name__ == '__main__':
    unittest.main()
