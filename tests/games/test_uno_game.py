import unittest
import numpy as np

from rlcard.games.uno.game import UnoGame as Game
from rlcard.games.uno.player import UnoPlayer as Player
from rlcard.games.uno.utils import ACTION_LIST
from rlcard.games.uno.utils import hand2dict, encode_hand, encode_target

class TestUnoMethods(unittest.TestCase):

    def test_get_player_num(self):
        game = Game()
        num_player = game.get_player_num()
        self.assertEqual(num_player, 2)

    def test_get_action_num(self):
        game = Game()
        action_num = game.get_action_num()
        self.assertEqual(action_num, 61)

    def test_init_game(self):
        game = Game()
        state, _ = game.init_game()
        total_cards = list(state['hand'] + state['others_hand'])
        self.assertGreaterEqual(len(total_cards), 14)

    def test_get_player_id(self):
        game = Game()
        _, player_id = game.init_game()
        current = game.get_player_id()
        self.assertEqual(player_id, current)


    def test_get_legal_actions(self):
        game = Game()
        game.init_game()
        actions = game.get_legal_actions()
        for action in actions:
            self.assertIn(action, ACTION_LIST)

    def test_step(self):
        game = Game()
        game.init_game()
        action = np.random.choice(game.get_legal_actions())
        state, next_player_id = game.step(action)
        current = game.round.current_player
        self.assertLessEqual(len(state['played_cards']), 2)
        self.assertEqual(next_player_id, current)

    def test_get_payoffs(self):
        game = Game()
        game.init_game()
        while not game.is_over():
            actions = game.get_legal_actions()
            action = np.random.choice(actions)
            state, _ = game.step(action)
            total_cards = len(state['hand']) + len(state['others_hand']) + len(state['played_cards']) + len(game.round.dealer.deck)
            self.assertEqual(total_cards, 108)
        payoffs = game.get_payoffs()
        total = 0
        for payoff in payoffs:
            total += payoff
        self.assertEqual(total, 0)

    def test_step_back(self):
        game = Game(allow_step_back=True)
        _, player_id = game.init_game()
        action = np.random.choice(game.get_legal_actions())
        game.step(action)
        game.step_back()
        self.assertEqual(game.round.current_player, player_id)
        self.assertEqual(len(game.history), 0)
        success = game.step_back()
        self.assertEqual(success, False)

    def test_hand2dict(self):
        hand_1 = ['y-1', 'r-8', 'b-9', 'y-reverse', 'r-skip']
        hand1_dict = hand2dict(hand_1)
        for _, count in hand1_dict.items():
            self.assertEqual(count, 1)
        hand_2 = ['y-4', 'y-4', 'r-skip', 'r-skip']
        hand2_dict = hand2dict(hand_2)
        for _, count in hand2_dict.items():
            self.assertEqual(count, 2)

    def test_encode_hand(self):
        hand1 = ['y-1', 'r-8', 'b-9', 'y-reverse', 'r-skip']
        encoded_hand1 = np.zeros((3, 4, 15), dtype=int)
        encode_hand(encoded_hand1, hand1)
        for index in range(15):
            total = 0
            for color in range(4):
                total += encoded_hand1[0][color][index] + encoded_hand1[1][color][index] + encoded_hand1[2][color][index]
            self.assertEqual(total, 4)
        hand2 = ['r-wild', 'g-wild_draw_4']
        encoded_hand2 = np.zeros((3, 4, 15), dtype=int)
        encode_hand(encoded_hand2, hand2)
        for color in range(4):
            self.assertEqual(encoded_hand2[1][color][-2], 1)
            self.assertEqual(encoded_hand2[1][color][-1], 1)

    def test_encode_target(self):
        encoded_target = np.zeros((4, 15), dtype=int)
        target = 'r-1'
        encode_target(encoded_target, target)
        self.assertEqual(encoded_target[0][1], 1)

    def test_player_get_player_id(self):
        player = Player(0)
        self.assertEqual(0, player.get_player_id())

if __name__ == '__main__':
    unittest.main()
