import unittest
import numpy as np
from rlcard.utils.utils import get_downstream_player_id, get_upstream_player_id
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.games.doudizhu.utils import get_landlord_score, encode_cards
from rlcard.games.doudizhu.utils import get_optimal_action


class TestDoudizhuMethods(unittest.TestCase):

    def test_get_player_num(self):
        game = Game()
        player_num = game.get_player_num()
        self.assertEqual(player_num, 3)

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 309)

    def test_init_game(self):
        game = Game()
        state, current_player = game.init_game()
        self.assertEqual(state['self'], current_player)
        self.assertEqual(state['landlord'], current_player)
        self.assertIs(state['played_cards'], None)

    def test_step(self):
        game = Game()
        state, _ = game.init_game()
        action = state['actions'][0]
        state, next_player_id = game.step(action)
        next_player = game.players[next_player_id]
        player_id = get_upstream_player_id(next_player, game.players)
        self.assertEqual(state['trace'][0][0], player_id)
        self.assertEqual(state['trace'][0][1], action)

    def test_get_player_id(self):
        game = Game()
        _, player_id = game.init_game()
        current_player_id = game.get_player_id()
        self.assertEqual(current_player_id, player_id)

    def test_proceed_game(self):
        game = Game()
        state, player_id = game.init_game()
        while not game.is_over():
            action = state['actions'][0]
            state, next_player_id = game.step(action)
            player = game.players[player_id]
            self.assertEqual(get_downstream_player_id(
                player, game.players), next_player_id)
            player_id = next_player_id
        for player_id in range(3):
            state = game.get_state(player_id)
            self.assertIsNone(state['actions'])

    def test_step_back(self):
        game = Game()
        state, player_id = game.init_game()
        action = state['actions'][0]
        game.step(action)
        game.step_back()
        self.assertEqual(game.current_player, player_id)
        self.assertEqual(len(game.histories), 0)

    def test_get_landlord_score(self):
        score_1 = get_landlord_score('56888TTQKKKAA222R')
        self.assertEqual(score_1, 12)

    def test_get_optimal_action(self):
        probs = np.zeros(309)
        probs[-1] = 0.5
        legal_actions = ['pass', '33344', 'BR']
        action = get_optimal_action(probs, legal_actions)
        self.assertEqual(action, 'pass')

    def test_encode_cards(self):
        plane = np.zeros((5, 15), dtype=int)
        plane[0] = np.ones(15, dtype=int)
        cards = '333BR'
        encode_cards(plane, cards)
        self.assertEqual(plane[3][0], 1)
        self.assertEqual(plane[1][13], 1)
        self.assertEqual(plane[1][14], 1)


if __name__ == '__main__':
    unittest.main()
