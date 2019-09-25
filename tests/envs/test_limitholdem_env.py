import unittest
import numpy as np

from rlcard.envs.limitholdem import LimitholdemEnv as Env
from rlcard.utils.utils import get_downstream_player_id
from rlcard.agents.random_agent import RandomAgent


class TestLimitholdemEnv(unittest.TestCase):

    def test_init_game_and_extract_state(self):
        env = Env()
        state, _ = env.init_game()
        self.assertEqual(state['obs'].size, 52)
        for action in state['legal_actions']:
            self.assertLess(action, env.action_num)

    def test_get_legal_actions(self):
        env = Env()
        env.init_game()
        legal_actions = env.get_legal_actions()
        for action in legal_actions:
            self.assertIn(action, env.actions)

    def test_decode_action(self):
        env = Env()
        state, _ = env.init_game()
        for action in state['legal_actions']:
            decoded = env.decode_action(action)
            self.assertIn(decoded, env.actions)

        decoded = env.decode_action(3)
        self.assertEqual(decoded, 'fold')

        env.step(0)
        decoded = env.decode_action(0)
        self.assertEqual(decoded, 'check')

    def test_step(self):
        env = Env()
        state, player_id = env.init_game()
        self.assertEqual(player_id, env.get_player_id())
        action = state['legal_actions'][0]
        _, player_id = env.step(action)
        self.assertEqual(player_id, env.get_player_id())

    def test_run(self):
        env = Env()
        agents = [RandomAgent(env.action_num) for _ in range(env.player_num)]
        env.set_agents(agents)
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 2)
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)


if __name__ == '__main__':
    unittest.main()
