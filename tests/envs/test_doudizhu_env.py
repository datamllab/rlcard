import unittest
from rlcard.envs.doudizhu import DoudizhuEnv as Env
from rlcard.utils.utils import get_downstream_player_id
from rlcard.agents.random_agent import RandomAgent


class TestDoudizhuEnv(unittest.TestCase):

    def test_init_game_and_extract_state(self):
        env = Env()
        state, _ = env.init_game()
        self.assertEqual(state['obs'].size, 450)

    def test_get_legal_actions(self):
        env = Env()
        env.set_agents([RandomAgent(309), RandomAgent(309), RandomAgent(309)])
        env.init_game()
        legal_actions = env.get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, 308)

    def test_step(self):
        env = Env()
        _, player_id = env.init_game()
        player = env.game.players[player_id]
        _, next_player_id = env.step(308)
        self.assertEqual(next_player_id, get_downstream_player_id(
            player, env.game.players))

    def test_run(self):
        env = Env()
        env.set_agents([RandomAgent(309), RandomAgent(309), RandomAgent(309)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 3)
        win = []
        for player_id, payoff in enumerate(payoffs):
            if payoff == 1:
                win.append(player_id)
        if len(win) == 1:
            self.assertEqual(env.game.players[win[0]].role, 'landlord')
        if len(win) == 2:
            self.assertEqual(env.game.players[win[0]].role, 'peasant')
            self.assertEqual(env.game.players[win[1]].role, 'peasant')

    def test_decode_action(self):
        env = Env()
        state, _ = env.init_game()
        for action in state['legal_actions']:
            decoded = env.decode_action(action)
            self.assertIn(decoded, env.game.state['actions'])

        state, _ = env.step(0)
        for action in range(309):
            if action not in state['legal_actions']:
                decoded = env.decode_action(action)
                self.assertEqual(decoded, 'pass')
                break

if __name__ == '__main__':
    unittest.main()
