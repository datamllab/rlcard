import unittest

from rlcard.envs.nolimitholdem import NolimitholdemEnv as Env
from rlcard.agents.random_agent import RandomAgent


class TestNolimitholdemEnv(unittest.TestCase):

    def test_init_game_and_extract_state(self):
        env = Env()
        state, _ = env.init_game()
        self.assertEqual(state['obs'].size, 54)
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

    def test_step_back(self):
        env = Env(allow_step_back=True)
        _, player_id = env.init_game()
        env.step(0)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = Env()
        with self.assertRaises(Exception):
            env.step_back()

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
