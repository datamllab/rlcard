import unittest
import numpy as np

from rlcard.games.gin_rummy.game import GinRummyGame as Game
from rlcard.games.gin_rummy.judge import GinRummyJudge
from rlcard.games.gin_rummy.action_event import score_player_1_action_id


class TestGinRummyGame(unittest.TestCase):

    def test_get_player_num(self):
        game = Game()
        player_num = game.get_player_num()
        self.assertEqual(player_num, 2)

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 110)

    def test_init_game(self):
        game = Game()
        state, current_player = game.init_game()
        opponent_player = (current_player + 1) % 2
        self.assertEqual(len(game.round.move_sheet), 1)
        self.assertIn(current_player, [0, 1])
        self.assertIn(game.round.dealer_id, [0, 1])
        self.assertEqual(len(game.actions), 0)
        self.assertEqual(len(game.round.players[current_player].hand), 11)
        self.assertEqual(len(game.round.players[opponent_player].hand), 10)
        self.assertEqual(opponent_player, game.round.dealer_id)
        self.assertEqual(len(game.round.dealer.shuffled_deck), 52)
        self.assertEqual(len(game.round.dealer.stock_pile), 31)
        self.assertEqual(state['player_id'], current_player)
        self.assertEqual(len(state['hand']), 11)

    def test_step(self):
        game = Game()
        judge = GinRummyJudge(game=game)
        _, current_player = game.init_game()
        opponent_player = (current_player + 1) % 2
        action = np.random.choice(judge.get_legal_actions())
        next_state, next_player = game.step(action)
        if not game.is_over():
            self.assertEqual(next_player, opponent_player)
        if not game.is_over():
            action = np.random.choice(judge.get_legal_actions())
            next_state, next_player = game.step(action)  # get card
            self.assertEqual(next_player, opponent_player)  # keep turn to put card

    def test_proceed_game(self):
        game = Game()
        judge = GinRummyJudge(game=game)
        game.init_game()
        while not game.is_over():
            legal_actions = judge.get_legal_actions()
            action = np.random.choice(legal_actions)
            state, _ = game.step(action)
        self.assertEqual(game.actions[-1].action_id, score_player_1_action_id)

    def test_get_state(self):
        game = Game()
        state, current_player = game.init_game()
        self.assertEqual(len(state), 6)


if __name__ == '__main__':
    unittest.main()
