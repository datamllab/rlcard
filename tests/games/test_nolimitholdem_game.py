import unittest

from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game
import numpy as np


class TestNolimitholdemMethods(unittest.TestCase):

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 103)

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)
        self.assertIn('call', state['legal_actions'])
        self.assertIn('fold', state['legal_actions'])
        self.assertIn('all-in', state['legal_actions'])
        for i in range(3, 99):
            self.assertIn(i, state['legal_actions'])

    def test_step(self):
        game = Game()

        # test raise
        _, player_id = game.init_game()
        init_raised = game.round.raised[player_id]
        game.step(10)
        step_raised = game.round.raised[player_id]
        self.assertEqual(init_raised + 10, step_raised)

        # test call
        game.init_game()
        init_not_raise_num = game.round.not_raise_num
        game.step('call')
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num + 1, step_not_raise_num)

        # test fold
        game.init_game()
        game.step('fold')
        self.assertTrue(game.round.player_folded)

        # test check
        game.init_game()
        game.step('call')
        game.step('check')
        self.assertEqual(game.round_counter, 1)

    def test_all_in(self):
        game = Game()

        _, player_id = game.init_game()
        game.step('all-in')
        step_raised = game.round.raised[player_id]
        self.assertEqual(99, step_raised)
        self.assertEqual(100, game.players[player_id].in_chips)
        self.assertEqual(0, game.players[player_id].remained_chips)

    def test_payoffs_1(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step('call')
        game.step(4)
        game.step('fold')
        self.assertTrue(game.is_over())
        self.assertListEqual([-2.0, 2.0], game.get_payoffs())

    def test_payoffs_2(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step('call')
        game.step(4)
        game.step('all-in')
        game.step('fold')
        self.assertTrue(game.is_over())
        self.assertListEqual([6.0, -6.0], game.get_payoffs())


if __name__ == '__main__':
    unittest.main()
