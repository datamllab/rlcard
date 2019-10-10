import unittest
import numpy as np

from rlcard.envs.blackjack import BlackjackEnv as Env
from rlcard.agents.random_agent import RandomAgent


class TestBlackjackEnv(unittest.TestCase):

    def test_init_and_extract_state(self):
        env = Env()
        state, _ = env.init_game()
        for score in state['obs']:
            self.assertLessEqual(score, 30)

    def test_decode_action(self):
        env = Env()
        self.assertEqual(env.decode_action(0), 'hit')
        self.assertEqual(env.decode_action(1), 'stand')

    def test_get_legal_actions(self):
        env = Env()
        actions = env.get_legal_actions()
        self.assertEqual(len(actions), 2)
        self.assertEqual(actions[0], 0)
        self.assertEqual(actions[1], 1)

    def test_get_payoffs(self):
        env = Env()
        for _ in range(100):
            env.init_game()
            while not env.is_over():
                action = np.random.choice([0, 1])
                env.step(action)
            payoffs = env.get_payoffs()
            for payoff in payoffs:
                self.assertIn(payoff, [-1, 1, 0])

    def test_step_back(self):
        env = Env(allow_step_back=True)
        _, player_id = env.init_game()
        env.step(1)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = Env()
        with self.assertRaises(Exception):
            env.step_back()

    def test_run(self):
        env = Env()
        env.set_agents([RandomAgent(2)])
        trajectories, _ = env.run(is_training=False)
        self.assertEqual(len(trajectories), 1)
        trajectories, _ = env.run(is_training=True, seed=1)
        self.assertEqual(len(trajectories), 1)

if __name__ == '__main__':
    unittest.main()
