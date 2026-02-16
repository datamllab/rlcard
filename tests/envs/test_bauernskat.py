'''
    File name: tests/envs/test_bauernskat_env.py
    Author: Oliver Czerwinski
    Date created: 08/12/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''
import unittest
import numpy as np
import random

import rlcard
from rlcard.agents.bauernskat.rule_agents import BauernskatRandomRuleAgent
from rlcard.games.bauernskat.action_event import DeclareTrumpAction, PlayCardAction
from rlcard.games.bauernskat.card import BauernskatCard
from rlcard.games.bauernskat.player import _CardColumn
from rlcard.games.bauernskat import config


class TestBauernskatEnv(unittest.TestCase):
    """
    Tests the BauernskatEnv.
    """

    def test_init_and_extract_state(self):
        """
        Tests initialization and the structure of the state.
        """
        
        env = rlcard.make('bauernskat')
        state, player_id = env.reset()

        self.assertEqual(player_id, 0)
        self.assertIn('obs', state)
        self.assertIn('legal_actions', state)
        
        obs = state['obs']
        
        expected_keys = [
            'my_layout_tensor', 'opponent_layout_tensor', 'unaccounted_cards_mask',
            'trick_card_ids', 'cemetery_card_ids', 'my_hidden_indicators', 
            'opponent_hidden_indicators', 'context', 'action_history'
        ]
        for key in expected_keys:
            self.assertIn(key, obs, f"Expected key '{key}' not found in observation.")

        self.assertEqual(obs['my_layout_tensor'].shape, (config.NUM_COLUMNS_PER_PLAYER, 2))
        self.assertEqual(obs['my_layout_tensor'].dtype, np.int32)
        self.assertEqual(obs['opponent_layout_tensor'].shape, (config.NUM_COLUMNS_PER_PLAYER, 2))
        self.assertEqual(obs['opponent_layout_tensor'].dtype, np.int32)
        self.assertEqual(obs['unaccounted_cards_mask'].shape, (32,))
        self.assertEqual(obs['unaccounted_cards_mask'].dtype, np.float32)

        self.assertEqual(obs['context'].shape, (11,))
        self.assertEqual(obs['my_hidden_indicators'].shape, (config.NUM_COLUMNS_PER_PLAYER,))
        self.assertEqual(obs['action_history'].shape, (config.HISTORY_SEQUENCE_LENGTH, config.HISTORY_FRAME_SIZE))
        self.assertEqual(obs['context'].dtype, np.float32)

    def test_decode_action(self):
        """
        Tests that action IDs are decoded into game actions.
        """
        
        env = rlcard.make('bauernskat')
        
        decoded_declare = env._decode_action(2)
        self.assertIsInstance(decoded_declare, DeclareTrumpAction)
        self.assertEqual(decoded_declare.trump_suit, 'H')
        
        decoded_play = env._decode_action(5)
        self.assertIsInstance(decoded_play, PlayCardAction)
        self.assertEqual(decoded_play.card.card_id, 0)

    def test_get_legal_actions(self):
        """
        Tests the correct set of legal actions.
        """
        
        env = rlcard.make('bauernskat')
        env.reset()
        legal_actions = env._get_legal_actions()
        
        self.assertEqual(len(legal_actions), 5)
        self.assertListEqual(list(legal_actions.keys()), [0, 1, 2, 3, 4])

    def test_get_payoffs_and_scores(self):
        """
        Tests the payoff and score after a random game.
        """
        
        env = rlcard.make('bauernskat')
        env.reset()
        
        while not env.is_over():
            legal_actions = list(env.get_state(env.get_player_id())['legal_actions'].keys())
            action = random.choice(legal_actions)
            env.step(action)
        
        payoffs = env.get_payoffs()
        self.assertIsInstance(payoffs, np.ndarray)
        self.assertEqual(len(payoffs), 2)
        self.assertIsInstance(payoffs[0], np.float32)
        self.assertAlmostEqual(payoffs[0], -payoffs[1])

    def test_run_with_random_agent(self):
        """
        Tests a full game with a random agent and the structure of the payoffs.
        """
        
        env = rlcard.make('bauernskat')
        
        env.set_agents([
            BauernskatRandomRuleAgent(),
            BauernskatRandomRuleAgent(),
        ])
        
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(trajectories), 2)
        self.assertIsInstance(payoffs, np.ndarray)
        self.assertEqual(len(payoffs), 2)

    def test_deterministic_run_with_seeded_custom_agent(self):
        """
        Tests a full game with a seedable custom rule agent.
        """
        
        env = rlcard.make('bauernskat')
        env.seed(21000)

        agent1 = BauernskatRandomRuleAgent(seed=21001)
        agent2 = BauernskatRandomRuleAgent(seed=21002)

        env.set_agents([agent1, agent2])

        _, payoffs = env.run(is_training=False)

        expected_payoffs = np.array([-100.0, 100.0], dtype=np.float32)
        np.testing.assert_array_equal(payoffs, expected_payoffs)

    def test_layout_tensor_mapping(self):
        """
        Tests the mapping of the game state layout tensors.
        """
        
        # Perfect information
        env = rlcard.make('bauernskat', config={'information_level': 'perfect'})
        env.reset()
        
        env.game.players[0].layout = [_CardColumn() for _ in range(config.NUM_COLUMNS_PER_PLAYER)]

        ace_spades = BauernskatCard('S', 'A')
        king_clubs = BauernskatCard('C', 'K')
        
        env.game.players[0].layout[0].open_card = ace_spades
        env.game.players[0].layout[3].open_card = None
        env.game.players[0].layout[5].open_card = king_clubs
        env.game.players[0].layout[5].closed_card = ace_spades
        
        state = env.get_state(player_id=0)
        layout_tensor = state['obs']['my_layout_tensor']
        
        self.assertEqual(layout_tensor[0, 0], ace_spades.card_id)
        self.assertEqual(layout_tensor[0, 1], 32)
        
        self.assertEqual(layout_tensor[3, 0], 32)
        self.assertEqual(layout_tensor[3, 1], 32)
        
        self.assertEqual(layout_tensor[5, 0], king_clubs.card_id)
        self.assertEqual(layout_tensor[5, 1], ace_spades.card_id)
    
    def test_perfect_information_mode(self):
        """
        Tests the effect of the information level.
        """
        
        # Normal
        env_normal = rlcard.make('bauernskat', config={'seed': 42})
        state_normal, _ = env_normal.reset()
        obs_normal = state_normal['obs']
        
        self.assertTrue(np.all(obs_normal['opponent_layout_tensor'][:, 1] == 32))
        self.assertEqual(np.sum(obs_normal['unaccounted_cards_mask']), 28.0)

        # Perfect
        env_perfect = rlcard.make('bauernskat', config={'seed': 42, 'information_level': 'perfect'})
        state_perfect, _ = env_perfect.reset()
        obs_perfect = state_perfect['obs']
        
        self.assertTrue(np.any(obs_perfect['opponent_layout_tensor'][:, 1] != 32))
        self.assertEqual(np.sum(obs_perfect['unaccounted_cards_mask']), 20.0)

    def test_extract_state_maps_full_game_state_correctly(self):
        """
        Tests a complex game state extraction.
        """
        env = rlcard.make('bauernskat', config={'information_level': 'perfect'})
        env.reset()
        game = env.game
        player0, player1 = game.players

        game.round.round_phase = 'play'
        game.round.trump_suit = 'H'
        game.round.current_player_id = 1
        game.round.trick_leader_id = 0
        game.round.tricks_played = 5
        player0.score = 35
        player1.score = 25
        
        p0_open = BauernskatCard('S', 'A')
        p0_hidden = BauernskatCard('C', '7')
        p1_open = BauernskatCard('C', 'K')
        p1_hidden = BauernskatCard('H', '8')
        trick_card = BauernskatCard('D', '10')
        cemetery_card = BauernskatCard('D', '7')

        player0.layout = [_CardColumn() for _ in range(8)]
        player1.layout = [_CardColumn() for _ in range(8)]
        player0.layout[0].open_card = p0_open
        player0.layout[2].closed_card = p0_hidden
        player1.layout[1].open_card = p1_open
        player1.layout[4].closed_card = p1_hidden
        game.round.trick_moves = [(0, trick_card)]
        game.round.played_cards = {cemetery_card}

        state = env.get_state(player_id=1)
        obs = state['obs']
        
        self.assertEqual(obs['my_layout_tensor'][1, 0], p1_open.card_id)
        self.assertEqual(obs['my_layout_tensor'][4, 1], p1_hidden.card_id)
        self.assertEqual(obs['opponent_layout_tensor'][0, 0], p0_open.card_id)
        self.assertEqual(obs['opponent_layout_tensor'][2, 1], p0_hidden.card_id)

        known_cards = {p0_open.card_id, p0_hidden.card_id, p1_open.card_id, 
                       p1_hidden.card_id, trick_card.card_id, cemetery_card.card_id}
        expected_mask = np.ones(32, dtype=np.float32)
        for card_id in known_cards:
            expected_mask[card_id] = 0.0
        np.testing.assert_array_equal(obs['unaccounted_cards_mask'], expected_mask)
        self.assertEqual(np.sum(obs['unaccounted_cards_mask']), 26.0)

        expected_context = np.array([
            0., 0., 1., 0., 0., 1.0, 1.0, 0.0, 
            25.0 / 480.0, 35.0 / 480.0, 5.0 / 16.0
        ], dtype=np.float32)
        np.testing.assert_array_almost_equal(obs['context'], expected_context)

    def test_get_scores(self):
        """
        Tests that get_scores() returns the current pips.
        """
        
        env = rlcard.make('bauernskat')
        env.reset()

        env.game.players[0].score = 42
        env.game.players[1].score = 18

        scores = env.get_scores()
        
        self.assertIsInstance(scores, np.ndarray)
        self.assertEqual(scores.dtype, np.int32)
        np.testing.assert_array_equal(scores, [42, 18])
    
    def test_asymmetric_information_tensors(self):
        """
        Tests asymmetric information levels between players.
        """
        
        # "perfect" "normal"
        env = rlcard.make('bauernskat', config={'information_level': {0: 'perfect', 1: 'normal'}})
        env.reset()
        
        env.game.players[1].layout[0].closed_card = BauernskatCard('H', 'K')
        
        state_p0 = env.get_state(0)
        opp_tensor_p0 = state_p0['obs']['opponent_layout_tensor']
        self.assertTrue(np.any(opp_tensor_p0[:, 1] != 32))
        
        state_p1 = env.get_state(1)
        opp_tensor_p1 = state_p1['obs']['opponent_layout_tensor']
        self.assertTrue(np.all(opp_tensor_p1[:, 1] == 32))

if __name__ == '__main__':
    unittest.main()