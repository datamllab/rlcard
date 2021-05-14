import unittest
import numpy as np

from rlcard.games.mahjong.game import MahjongGame as Game
from rlcard.games.mahjong.player import MahjongPlayer as Player

class TestMahjongMethods(unittest.TestCase):

    def test_get_num_players(self):
        game = Game()
        num_players = game.get_num_players()
        self.assertEqual(num_players, 4)

    def test_get_num_actions(self):
        game = Game()
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, 38)

    def test_init_game(self):
        game = Game()
        state, _ = game.init_game()
        total_cards = list(state['current_hand'])
        self.assertGreaterEqual(len(total_cards), 14)

    def test_get_player_id(self):
        game = Game()
        _, player_id = game.init_game()
        current = game.get_player_id()
        self.assertEqual(player_id, current)


    def test_get_legal_actions(self):
        game = Game()
        state, _ = game.init_game()
        actions = game.get_legal_actions(state)
        for action in actions:
            self.assertIn(action, state['current_hand'])

    def test_step(self):
        game = Game()
        state, _ = game.init_game()
        action = np.random.choice(game.get_legal_actions(state))
        state, next_player_id = game.step(action)
        current = game.round.current_player
        self.assertLessEqual(len(state['current_hand']), 14)
        self.assertEqual(next_player_id, current)

    def test_get_payoffs(self):
        game = Game()
        state, _ = game.init_game()
        while not game.is_over():
            actions = game.get_legal_actions(state)
            action = np.random.choice(actions)
            state, _ = game.step(action)
            total_cards = len(state['current_hand'])
            self.assertLessEqual(total_cards, 14)
        win = game.is_over()
        self.assertEqual(win, True)

    def test_step_back(self):
        game = Game(allow_step_back=True)
        state, player_id = game.init_game()
        action = np.random.choice(game.get_legal_actions(state))
        game.step(action)
        game.step_back()
        self.assertEqual(game.round.current_player, player_id)
        self.assertEqual(len(game.history), 0)
        success = game.step_back()
        self.assertEqual(success, False)

    def test_player_get_player_id(self):
        player = Player(0, np.random.RandomState())
        self.assertEqual(0, player.get_player_id())

if __name__ == '__main__':
    unittest.main()
