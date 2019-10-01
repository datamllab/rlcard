import unittest

from rlcard.games.leducholdem.game import LeducholdemGame as Game

class TestLeducholdemMethods(unittest.TestCase):

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 4)

    def test_init_game(self):

        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)
        self.assertIn('raise', state['legal_actions'])
        self.assertIn('fold', state['legal_actions'])
        self.assertIn('check', state['legal_actions'])

    def test_step(self):
        game = Game()

        # test raise
        game.init_game()
        init_raised = game.round.have_raised
        game.step('raise')
        step_raised = game.round.have_raised
        self.assertEqual(init_raised + 1, step_raised)

        # test fold
        game.init_game()
        game.step('fold')
        self.assertTrue(game.round.player_folded)

        # test call
        game.init_game()
        game.step('raise')
        game.step('call')
        self.assertEqual(game.round_counter, 1)

        # test check
        game.init_game()
        game.step('check')
        game.step('check')
        self.assertEqual(game.round_counter, 1)

    def test_step_back(self):
        game = Game(allow_step_back=True)
        state, player_id = game.init_game()
        action = state['legal_actions'][0]
        game.step(action)
        game.step_back()
        self.assertEqual(game.game_pointer, player_id)
        self.assertEqual(game.step_back(), False)


if __name__ == '__main__':
    unittest.main()
