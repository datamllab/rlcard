import unittest
import numpy as np

from rlcard.games.blackjack.game import BlackjackGame as Game
from rlcard.envs.blackjack import DEFAULT_GAME_CONFIG

class TestBlackjackGame(unittest.TestCase):

    def test_get_num_players(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        num_players = game.get_num_players()
        self.assertEqual(num_players, 1)

    def test_get_num_actions(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, 2)

    def test_init_game(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        state, current_player = game.init_game()
        self.assertEqual(len(game.history), 0)
        self.assertEqual(current_player, 0)
        self.assertEqual(game.winner['dealer'], 0)
        self.assertEqual(len(state['state'][0]), len(state['state'][1])+1)

    def test_step(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()
        next_state, next_player = game.step('hit')
        self.assertEqual(next_player, 0)
        if game.players[0].status != 'bust':
            self.assertEqual(len(game.dealer.hand), len(next_state['state'][1])+1)
        else:
            self.assertEqual(len(game.dealer.hand), len(next_state['state'][1]))
        next_state, _ = game.step('stand')
        self.assertEqual(len(next_state['state'][0]), len(game.players[0].hand))

    def test_proceed_game(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()
        while not game.is_over():
            action = np.random.choice(['hit', 'action'])
            state, _ = game.step(action)
        self.assertEqual(len(state['state'][1]), len(game.dealer.hand))

    def test_step_back(self):
        game = Game(allow_step_back=True)
        game.configure(DEFAULT_GAME_CONFIG)
        state, _ = game.init_game()
        init_hand = state['state'][0]
        game.step('hit')
        game.step_back()
        test_hand = game.get_state(0)['state'][0]
        self.assertEqual(init_hand, test_hand)
        self.assertEqual(len(game.history), 0)
        success = game.step_back()
        self.assertEqual(success, False)

    def test_get_state(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()
        self.assertEqual(len(game.get_state(0)['state'][1]), 1)
        game.step('stand')
        self.assertGreater(len(game.get_state(0)['state'][1]), 1)

if __name__ == '__main__':
    unittest.main()
