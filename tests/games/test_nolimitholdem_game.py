import unittest

from rlcard.games.limitholdem.player import PlayerStatus
from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game, Stage
import numpy as np
from rlcard.utils import seeding

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
        game.step(Action.CHECK_CALL)
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num + 1, step_not_raise_num)

        # test fold
        _, player_id = game.init_game()
        game.step(Action.FOLD)

        self.assertEqual(PlayerStatus.FOLDED, game.players[player_id].status)

        # test check
        game.init_game()
        game.step(Action.CHECK_CALL)

    def test_bet_more_than_chips(self):
        game = Game()

        # test check
        game.init_game()
        player = game.players[0]
        in_chips = player.in_chips
        player.bet(50)
        self.assertEqual(50+in_chips, player.in_chips)

        player.bet(150)
        self.assertEqual(100, player.in_chips)

    def test_step_2(self):
        game = Game()

        # test check
        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.FLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.TURN, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

    def test_step_3_players(self):
        game = Game(num_players=3)

        # test check
        _, first_player_id = game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.FOLD)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.FLOP, game.stage)
        self.assertEqual((first_player_id - 2) % 3, game.round.game_pointer)
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.TURN, game.stage)
        self.assertEqual((first_player_id - 2) % 3, game.round.game_pointer)
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

    def test_auto_step(self):
        game = Game()

        game.init_game()
        self.assertEqual(Stage.PREFLOP, game.stage)
        game.step(Action.ALL_IN)
        game.step(Action.CHECK_CALL)

        self.assertEqual(Stage.RIVER, game.stage)

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
        game.step(Action.CHECK_CALL)
        game.step(Action.CHECK_CALL)
        self.assertEqual(game.round_counter, 1)

        game.step(Action.CHECK_CALL)
        game.step(Action.ALL_IN)
        self.assertListEqual([Action.FOLD, Action.CHECK_CALL], game.get_legal_actions())
        game.step(Action.CHECK_CALL)
        self.assertEqual(game.round_counter, 4)
        self.assertEqual(200, game.dealer.pot)

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

        game.step(Action.CHECK_CALL)
        player_id = game.round.game_pointer
        game.step(Action.RAISE_POT)
        step_raised = game.round.raised[player_id]
        self.assertEqual(32, step_raised)

    def test_raise_half_pot(self):
        game = Game()

        _, player_id = game.init_game()
        self.assertNotIn(Action.RAISE_HALF_POT, game.get_legal_actions()) # Half pot equals call
        game.step(Action.CHECK_CALL)
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
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_HALF_POT)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertEqual(2, len(game.get_payoffs()))
        #self.assertListEqual([-2.0, 2.0], game.get_payoffs())

    def test_payoffs_2(self):
        game = Game()
        np.random.seed(0)
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.RAISE_POT)
        game.step(Action.ALL_IN)
        game.step(Action.FOLD)
        self.assertTrue(game.is_over())
        self.assertEqual(2, len(game.get_payoffs()))
        #self.assertListEqual([6.0, -6.0], game.get_payoffs())

    def test_all_in_to_call(self):
        game = Game()
        game.init_chips = [50, 100]
        game.dealer_id = 0
        game.init_game()
        game.step(Action.CHECK_CALL)
        game.step(Action.ALL_IN)
        game.step(Action.CHECK_CALL)
        self.assertTrue(game.is_over())


if __name__ == '__main__':
    unittest.main()
