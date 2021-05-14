import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.games.uno.utils import ACTION_LIST
from .determism_util import is_deterministic


class TestUnoEnv(unittest.TestCase):

    def test_reset_and_extract_state(self):
        env = rlcard.make('uno')
        state, _ = env.reset()
        self.assertEqual(state['obs'].size, 240)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('uno'))

    def test_get_legal_actions(self):
        env = rlcard.make('uno')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, 60)

    def test_step(self):
        env = rlcard.make('uno')
        state, _ = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.game.round.current_player)

    def test_step_back(self):
        env = rlcard.make('uno', config={'allow_step_back':True})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        env.step_back()
        self.assertEqual(env.game.round.current_player, player_id)

        env = rlcard.make('uno', config={'allow_step_back':False})
        state, player_id = env.reset()
        action = np.random.choice(list(state['legal_actions'].keys()))
        env.step(action)
        # env.step_back()
        self.assertRaises(Exception, env.step_back)

    def test_run(self):
        env = rlcard.make('uno')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 2)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)
        trajectories, payoffs = env.run(is_training=True)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)

    def test_decode_action(self):
        env = rlcard.make('uno')
        env.reset()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            decoded = env._decode_action(legal_action)
            self.assertLessEqual(decoded, ACTION_LIST[legal_action])

    def test_get_perfect_information(self):
        env = rlcard.make('uno')
        _, player_id = env.reset()
        self.assertEqual(player_id, env.get_perfect_information()['current_player'])
if __name__ == '__main__':
    unittest.main()
