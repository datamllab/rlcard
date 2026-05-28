import unittest
import numpy as np

from rlcard.games.mahjong.game import MahjongGame as Game
from rlcard.games.mahjong.card import MahjongCard as Card
from rlcard.games.mahjong.judger import MahjongJudger as Judger
from rlcard.games.mahjong.player import MahjongPlayer as Player


def _card(card_type, trait):
    return Card(card_type, trait)


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

    def test_judge_hu_requires_pair_with_four_exposed_sets(self):
        judger = Judger(np.random.RandomState())
        player = Player(0, np.random.RandomState())
        player.pile = [
            [_card('characters', '1')] * 3,
            [_card('characters', '2')] * 3,
            [_card('characters', '3')] * 3,
            [_card('dots', '5')] * 3,
        ]
        player.hand = [_card('dots', '6'), _card('bamboo', '4')]

        win, value = judger.judge_hu(player)

        self.assertFalse(win)
        self.assertEqual(value, 4)

    def test_judge_hu_allows_four_exposed_sets_with_pair(self):
        judger = Judger(np.random.RandomState())
        player = Player(0, np.random.RandomState())
        player.pile = [
            [_card('characters', '1')] * 3,
            [_card('characters', '2')] * 3,
            [_card('characters', '3')] * 3,
            [_card('dots', '5')] * 3,
        ]
        player.hand = [_card('bamboo', '4'), _card('bamboo', '4')]

        win, value = judger.judge_hu(player)

        self.assertTrue(win)
        self.assertEqual(value, 4)

if __name__ == '__main__':
    unittest.main()
