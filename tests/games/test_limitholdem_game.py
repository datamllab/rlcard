import unittest
import numpy as np

from rlcard.games.limitholdem.game import LimitholdemGame as Game
from rlcard.games.limitholdem.player import LimitholdemPlayer as Player


class TestLimitholdemMethods(unittest.TestCase):

    def test_get_player_num(self):
        game = Game()
        player_num = game.get_player_num()
        self.assertEqual(player_num, 2)

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 4)

    def test_init_game(self):
        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)
        self.assertIn('call', state['legal_actions'])
        self.assertIn('raise', state['legal_actions'])
        self.assertIn('fold', state['legal_actions'])

    def test_step(self):
        game = Game()

        # test raise
        game.init_game()
        init_raised = game.round.have_raised
        game.step('raise')
        step_raised = game.round.have_raised
        self.assertEqual(init_raised+1, step_raised)

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

        # test play 4 rounds
        game.init_game()
        for i in range(19):
            if (i+1) % 5 == 0:
                game.step('call')
            else:
                game.step('raise')
            self.assertEqual(game.is_over(), False)
        game.step('call')
        self.assertEqual(game.is_over(), True)

        # Test illegal actions
        game.init_game()
        with self.assertRaises(Exception):
            game.step('check')

        # Test the upper limit of raise
        game.init_game()
        for _ in range(4):
            game.step('raise')

        legal_actions = game.get_legal_actions()
        self.assertNotIn('raise', legal_actions)


    def test_step_back(self):
        game = Game(allow_step_back=True)
        game.init_game()
        self.assertEqual(game.step_back(), False)
        index = 0
        previous = None
        while not game.is_over():
            index += 1
            legal_actions = game.get_legal_actions()
            if index == 2:
                result = game.step_back()
                now = game.get_player_id()
                if result:
                    self.assertEqual(previous, now)
                else:
                    self.assertEqual(len(game.history), 0)
                break
            previous = game.get_player_id()
            action = np.random.choice(legal_actions)
            game.step(action)

    def test_payoffs(self):
        game = Game()
        np.random.seed(0)
        for _ in range(5):
            game.init_game()
            while not game.is_over():
                legal_actions = game.get_legal_actions()
                action = np.random.choice(legal_actions)
                game.step(action)
            payoffs = game.get_payoffs()
            total = 0
            for payoff in payoffs:
                total += payoff
            self.assertEqual(total, 0)

    def test_get_player_id(self):
        player = Player(3)
        self.assertEqual(player.get_player_id(), 3)


if __name__ == '__main__':
    unittest.main()
