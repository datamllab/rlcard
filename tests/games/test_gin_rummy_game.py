'''
    File name: test_gin_rummy_game.py
    Author: William Hale
    Date created: 3/11/2020
'''

import unittest
import numpy as np

from rlcard.games.gin_rummy.game import GinRummyGame as Game
from rlcard.games.gin_rummy.judge import GinRummyJudge
from rlcard.games.gin_rummy.utils.action_event import score_player_1_action_id
from rlcard.games.gin_rummy.utils.action_event import draw_card_action_id, pick_up_discard_action_id
from rlcard.games.gin_rummy.utils.action_event import declare_dead_hand_action_id
from rlcard.games.gin_rummy.utils.action_event import gin_action_id, discard_action_id, knock_action_id

discard_action_ids = list(range(discard_action_id, discard_action_id + 52))
knock_action_ids = list(range(knock_action_id, knock_action_id + 52))
put_action_ids = [gin_action_id] + discard_action_ids + knock_action_ids
get_action_ids = [draw_card_action_id, pick_up_discard_action_id, declare_dead_hand_action_id]


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
        self.assertEqual(opponent_player, game.round.dealer_id)  # opponent_player is dealer
        self.assertEqual(len(game.round.players[opponent_player].hand), 10)  # dealer has 10 cards
        self.assertEqual(len(game.round.players[current_player].hand), 11)  # current_player has 11 cards
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
        self.assertIn(action.action_id, put_action_ids)  # should be a put action
        next_state, next_player = game.step(action)
        if not game.is_over():
            self.assertEqual(next_player, opponent_player)
        if not game.is_over():
            action = np.random.choice(judge.get_legal_actions())
            self.assertIn(action.action_id, get_action_ids)  # should be a get action
            next_state, next_player = game.step(action)
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
