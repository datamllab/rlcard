import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent
from .determism_util import is_deterministic

class TestBlackjackEnv(unittest.TestCase):

    def test_init_and_extract_state(self):
        env = rlcard.make('blackjack')
        state, _ = env.reset()
        for score in state['obs']:
            self.assertLessEqual(score, 30)

    def test_is_deterministic(self):
        self.assertTrue(is_deterministic('blackjack'))

    def test_decode_action(self):
        env = rlcard.make('blackjack')
        self.assertEqual(env._decode_action(0), 'hit')
        self.assertEqual(env._decode_action(1), 'stand')

    def test_get_legal_actions(self):
        env = rlcard.make('blackjack')
        actions = env._get_legal_actions()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0], 0)
        self.assertEqual(actions[1], 1)

    def test_get_payoffs(self):
        env = rlcard.make('blackjack')
        for _ in range(100):
            env.reset()
            while not env.is_over():
                action = np.random.choice([0, 1])
                env.step(action)
            payoffs = env.get_payoffs()
            for payoff in payoffs:
                self.assertIn(payoff, [-1, 1, 0])

    def test_step_back(self):
        env = rlcard.make('blackjack', config={'allow_step_back':True})
        _, player_id = env.reset()
        env.step(1)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = rlcard.make('blackjack')
        with self.assertRaises(Exception):
            env.step_back()

    def test_multiplayers(self):
        env = rlcard.make('blackjack', config={'game_num_players':5})
        num_players = env.game.get_num_players()
        self.assertEqual(num_players, 5)

    def test_run(self):
        env = rlcard.make('blackjack')
        env.set_agents([RandomAgent(env.num_actions)])
        trajectories, _ = env.run(is_training=False)
        self.assertEqual(len(trajectories), 1)
        trajectories, _ = env.run(is_training=True)
        self.assertEqual(len(trajectories), 1)

if __name__ == '__main__':
    unittest.main()
