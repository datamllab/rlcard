import unittest

import rlcard
from rlcard.utils.utils import get_downstream_player_id
from rlcard.agents.random_agent import RandomAgent


class TestDoudizhuEnv(unittest.TestCase):

    def test_init_game_and_extract_state(self):
        env = rlcard.make('doudizhu')
        state, _ = env.init_game()
        self.assertEqual(state['obs'].size, 450)

    def test_get_legal_actions(self):
        env = rlcard.make('doudizhu')
        env.set_agents([RandomAgent(env.action_num) for _ in range(env.player_num)])
        env.init_game()
        legal_actions = env._get_legal_actions()
        for legal_action in legal_actions:
            self.assertLessEqual(legal_action, env.action_num-1)

    def test_step(self):
        env = rlcard.make('doudizhu')
        _, player_id = env.init_game()
        player = env.game.players[player_id]
        _, next_player_id = env.step(env.action_num-1)
        self.assertEqual(next_player_id, get_downstream_player_id(
            player, env.game.players))

    def test_step_back(self):
        env = rlcard.make('doudizhu', config={'allow_step_back':True})
        _, player_id = env.init_game()
        env.step(2)
        _, back_player_id = env.step_back()
        self.assertEqual(player_id, back_player_id)
        self.assertEqual(env.step_back(), False)

        env = rlcard.make('doudizhu')
        with self.assertRaises(Exception):
            env.step_back()

    def test_run(self):
        env = rlcard.make('doudizhu')
        env.set_agents([RandomAgent(env.action_num) for _ in range(env.player_num)])
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
        env = rlcard.make('doudizhu')
        env.init_game()
        env.game.state['actions'] = ['33366', '33355']
        env.game.judger.playable_cards[0] = ['5', '6', '55', '555', '33366', '33355']
        decoded = env._decode_action(54)
        self.assertEqual(decoded, '33366')
        env.game.state['actions'] = ['444', '44466', '44455']
        decoded = env._decode_action(29)
        self.assertEqual(decoded, '444')

if __name__ == '__main__':
    unittest.main()
