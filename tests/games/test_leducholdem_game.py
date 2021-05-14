import unittest
import numpy as np

from rlcard.games.leducholdem.game import LeducholdemGame as Game
from rlcard.games.leducholdem.player import LeducholdemPlayer as Player
from rlcard.games.leducholdem.judger import LeducholdemJudger as Judger
from rlcard.games.base import Card

class TestLeducholdemMethods(unittest.TestCase):

    def test_get_num_actions(self):
        game = Game()
        num_actions = game.get_num_actions()
        self.assertEqual(num_actions, 4)

    def test_init_game(self):

        game = Game()
        state, player_id = game.init_game()
        test_id = game.get_player_id()
        self.assertEqual(test_id, player_id)
        self.assertIn('raise', state['legal_actions'])
        self.assertIn('fold', state['legal_actions'])
        self.assertIn('call', state['legal_actions'])

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
        game.step('call')
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

    def test_judge_game(self):
        np_random = np.random.RandomState()
        players = [Player(0, np_random), Player(1, np_random)]
        players[0].in_chips = 10
        players[1].in_chips = 10

        # Test hand is equal
        players[0].hand = Card('S', 'J')
        players[1].hand = Card('H', 'J')
        public_card = Card('S', 'Q')
        payoffs = Judger.judge_game(players, public_card)
        self.assertEqual(payoffs[0], 0)
        self.assertEqual(payoffs[1], 0)

        # Test one player get a pair
        players[0].hand = Card('S', 'J')
        players[1].hand = Card('S', 'Q')
        public_card = Card('H', 'J')
        payoffs = Judger.judge_game(players, public_card)
        self.assertEqual(payoffs[0], 10.0)
        self.assertEqual(payoffs[1], -10.0)

        # Other cases
        # Test one player get a pair
        players[0].hand = Card('S', 'J')
        players[1].hand = Card('S', 'Q')
        public_card = Card('H', 'K')
        payoffs = Judger.judge_game(players, public_card)
        self.assertEqual(payoffs[0], -10.0)
        self.assertEqual(payoffs[1], 10.0)

    def test_player_get_player_id(self):
        player = Player(0, np.random.RandomState())
        self.assertEqual(0, player.get_player_id())

    def test_is_over(self):
        game = Game()
        game.init_game()
        game.step('call')
        game.step('check')
        game.step('check')
        game.step('check')
        self.assertEqual(game.is_over(), True)




if __name__ == '__main__':
    unittest.main()
