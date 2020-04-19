import unittest

from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game, Stage
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

    def test_step(self):
        game = Game()

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

    def test_step_2(self):
        game = Game()

        # test check
        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage.PREFLOP)
        game.step('call')
        game.step('raise-pot')
        game.step('call')

        self.assertEqual(Stage.FLOP, game.stage.FLOP)
        game.step('check')
        game.step('check')

        self.assertEqual(Stage.TURN, game.stage.TURN)
        game.step('check')
        game.step('check')

        self.assertEqual(Stage.RIVER, game.stage.RIVER)

    def test_all_in(self):
        game = Game()

        _, player_id = game.init_game()
        game.step('all-in')
        step_raised = game.round.raised[player_id]
        self.assertEqual(100, step_raised)
        self.assertEqual(100, game.players[player_id].in_chips)
        self.assertEqual(0, game.players[player_id].remained_chips)

    def test_all_in_rounds(self):
        game = Game()

        game.init_game()
        game.step('call')
        game.step('check')
        self.assertEqual(game.round_counter, 1)
        self.assertListEqual(['fold', 'check', 'raise-half-pot', 'raise-pot', 'all-in'], game.get_legal_actions())

        game.step('check')
        game.step('all-in')
        self.assertListEqual(['call', 'fold'], game.get_legal_actions())
        game.step('call')
        self.assertEqual(game.round_counter, 2)
        self.assertListEqual([], game.get_legal_actions())

    def test_wrong_steps(self):
        game = Game()

        game.init_game()
        self.assertRaises(Exception, game.step, 'check')

    def test_raise_pot(self):
        game = Game()

        _, player_id = game.init_game()
        game.step('raise-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step('raise-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(8, step_raised)

        player_id = game.round.game_pointer
        game.step('raise-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(16, step_raised)

        game.step('call')
        player_id = game.round.game_pointer
        game.step('raise-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(32, step_raised)

    def test_raise_half_pot(self):
        game = Game()

        _, player_id = game.init_game()
        game.step('raise-half-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(2, step_raised)

        player_id = game.round.game_pointer
        game.step('raise-half-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step('raise-half-pot')
        step_raised = game.round.raised[player_id]
        self.assertEqual(5, step_raised)

    def test_payoffs_1(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step('call')
        game.step('raise-half-pot')
        game.step('fold')
        self.assertTrue(game.is_over())
        self.assertListEqual([-2.0, 2.0], game.get_payoffs())

    def test_payoffs_2(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step('call')
        game.step('raise-pot')
        game.step('all-in')
        game.step('fold')
        self.assertTrue(game.is_over())
        self.assertListEqual([6.0, -6.0], game.get_payoffs())


if __name__ == '__main__':
    unittest.main()
