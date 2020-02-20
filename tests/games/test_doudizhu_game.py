import unittest
import numpy as np
import functools

from rlcard.utils.utils import get_downstream_player_id, get_upstream_player_id
from rlcard.games.doudizhu.game import DoudizhuGame as Game
from rlcard.games.doudizhu.utils import get_landlord_score, encode_cards
from rlcard.games.doudizhu.utils import get_optimal_action, doudizhu_sort_str
from rlcard.games.doudizhu.judger import DoudizhuJudger as Judger


class TestDoudizhuGame(unittest.TestCase):

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
        total_cards = list(state['current_hand'] + state['others_hand'])
        total_cards.sort(key=functools.cmp_to_key(doudizhu_sort_str))
        deck = list(game.round.deck_str)
        self.assertEqual(state['self'], current_player)
        self.assertEqual(state['landlord'], current_player)
        self.assertIs(len(state['played_cards']), 0)
        self.assertEqual(len(total_cards), 54)
        self.assertListEqual(total_cards, deck)

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
            action = np.random.choice(list(state['actions']))
            state, next_player_id = game.step(action)
            player = game.players[player_id]
            self.assertEqual(get_downstream_player_id(
                player, game.players), next_player_id)
            player_id = next_player_id
            if not game.is_over():
                self.assertIsNotNone(state['actions'])
        for player_id in range(3):
            state = game.get_state(player_id)
            self.assertIsNone(state['actions'])

    def test_step_back(self):
        #case 1: action, stepback
        game = Game(allow_step_back=True)
        state, player_id = game.init_game()
        action = state['actions'][0]
        playable_cards = game.judger.playable_cards
        game.step(action)
        game.step_back()
        self.assertEqual(game.judger.playable_cards, playable_cards)
        self.assertEqual(game.round.greater_player, None)
        self.assertEqual(game.round.current_player, player_id)
        self.assertEqual(len(game.history), 0)
        game.state['actions'].sort()
        state['actions'].sort()
        self.assertEqual(game.state, state)
        self.assertEqual(game.step_back(), False)

        #case 2: action, pass, stepback
        game = Game(allow_step_back=True)
        state, player_id = game.init_game()
        action = state['actions'][0]
        game.step(action)
        actions = game.state['actions']
        playable_cards = game.judger.playable_cards
        played_cards = game.players[game.round.current_player].played_cards
        game.step('pass')
        game.step_back()
        #judger.playable_cards should be the same
        self.assertEqual(game.judger.playable_cards, playable_cards)
        #players[current_player].played_cards should be the same
        self.assertEqual(game.players[game.round.current_player].played_cards, played_cards)
        #greater_player should be the same
        self.assertEqual(game.round.greater_player.player_id, 0)
        actions.sort()
        game.state['actions'].sort()
        #actions should be the same after step_back()
        self.assertEqual(game.state['actions'], actions)

        #case 3: action, pass, pass, action, stepback
        game = Game(allow_step_back=True)
        state, player_id = game.init_game()
        action = state['actions'][0]
        game.step(action)
        game.step('pass')
        game.step('pass')
        actions = game.state['actions']
        playable_cards = game.judger.playable_cards
        played_cards = game.players[game.round.current_player].played_cards
        game.step(actions[0])
        game.step_back()
        #judger.playable_cards should be the same
        self.assertEqual(game.judger.playable_cards, playable_cards)
        #players[current_player].played_cards should be the same
        self.assertEqual(game.players[game.round.current_player].played_cards, played_cards)
        #greater_player should be the same
        self.assertEqual(game.round.greater_player.player_id, 0)
        actions.sort()
        game.state['actions'].sort()
        #actions should be the same after step_back()
        self.assertEqual(game.state['actions'], actions)
        game.step_back()
        #greater_player should be the same
        self.assertEqual(game.round.greater_player.player_id, 0)

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

    def test_judge_payoffs(self):
        payoffs = Judger.judge_payoffs(0, 0)
        self.assertEqual(payoffs[0], 1)
        payoffs = Judger.judge_payoffs(2, 0)
        self.assertEqual(payoffs[0], 1)
        self.assertEqual(payoffs[1], 1)

if __name__ == '__main__':
    unittest.main()
