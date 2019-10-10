import unittest

from rlcard.games.nolimitholdem.game import NolimitholdemGame as Game

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
        for i in range(3,100):
            self.assertIn(i , state['legal_actions'])

    def test_step(self):
        game = Game()

        # test raise
        _, player_id = game.init_game()
        init_raised = game.round.raised[player_id]
        game.step(10)
        step_raised = game.round.raised[player_id]
        self.assertEqual(init_raised+10, step_raised)

        # test call
        game.init_game()
        init_not_raise_num = game.round.not_raise_num
        game.step('call')
        step_not_raise_num = game.round.not_raise_num
        self.assertEqual(init_not_raise_num+1, step_not_raise_num)

        # test fold
        game.init_game()
        game.step('fold')
        self.assertTrue(game.round.player_folded)

        # test check
        game.init_game()
        game.step('call')
        game.step('check')
        self.assertEqual(game.round_counter, 1)

if __name__ == '__main__':
    unittest.main()

