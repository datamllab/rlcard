import unittest

from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game, Stage
import numpy as np

from rlcard.games.nolimitholdem.round import Action


class TestNolimitholdemMethods(unittest.TestCase):

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
        game.step(Action.CALL)
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num + 1, step_not_raise_num)

        # test fold
        game.init_game()
        game.step(Action.FOLD)
        self.assertTrue(game.round.player_folded)

        # test check
        game.init_game()
        game.step(Action.CALL)
        game.step(Action.CHECK)
        self.assertEqual(game.round_counter, 1)

    def test_step_2(self):
        game = Game()

        # test check
        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage.PREFLOP)
        game.step(Action.CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.CALL)

        self.assertEqual(Stage.FLOP, game.stage.FLOP)
        game.step(Action.CHECK)
        game.step(Action.CHECK)

        self.assertEqual(Stage.TURN, game.stage.TURN)
        game.step(Action.CHECK)
        game.step(Action.CHECK)

        self.assertEqual(Stage.RIVER, game.stage.RIVER)

    def test_all_in(self):
        game = Game()

        _, player_id = game.init_game()
        game.step(Action.ALL_IN)
        step_raised = game.round.raised[player_id]
        self.assertEqual(100, step_raised)
        self.assertEqual(100, game.players[player_id].in_chips)
        self.assertEqual(0, game.players[player_id].remained_chips)

    def test_all_in_rounds(self):
        game = Game()

        game.init_game()
        game.step(Action.CALL)
        game.step(Action.CHECK)
        self.assertEqual(game.round_counter, 1)
        self.assertTrue(Action.CALL not in game.get_legal_actions())

        game.step(Action.CHECK)
        game.step(Action.ALL_IN)
        self.assertListEqual([Action.CALL, Action.FOLD], game.get_legal_actions())
        game.step(Action.CALL)
        self.assertEqual(game.round_counter, 2)
        # SHOULD FINISH THE GAME, NOT WAIT FOR AN ACTION
        # self.assertListEqual([], game.get_legal_actions())

    def test_wrong_steps(self):
        game = Game()

        game.init_game()
        self.assertRaises(Exception, game.step, Action.CHECK)

    def test_raise_pot(self):
        game = Game()

        _, player_id = game.init_game()
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(8, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(16, step_raised)

        game.step(Action.CALL)
        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(32, step_raised)

    def test_raise_half_pot(self):
        game = Game()

        _, player_id = game.init_game()
        game.step(Action.RAISE_HALF_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(2, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_HALF_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(4, step_raised)

        player_id = game.round.game_pointer
        game.step(Action.RAISE_HALF_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(5, step_raised)

    def test_payoffs_1(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step(Action.CALL)
        game.step(Action.RAISE_HALF_POT)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertListEqual([-2.0, 2.0], game.get_payoffs())

    def test_payoffs_2(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step(Action.CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.ALL_IN)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertListEqual([6.0, -6.0], game.get_payoffs())


if __name__ == '__main__':
    unittest.main()
