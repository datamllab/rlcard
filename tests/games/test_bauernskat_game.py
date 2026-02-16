'''
    File name: tests/games/test_bauernskat_card.py
    Author: Oliver Czerwinski
    Date created: 07/29/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

import unittest
import numpy as np

from rlcard.games.bauernskat import config

from rlcard.games.bauernskat.card import BauernskatCard
from rlcard.games.bauernskat.action_event import ActionEvent, DeclareTrumpAction, PlayCardAction
from rlcard.games.bauernskat.player import BauernskatPlayer, _CardColumn
from rlcard.games.bauernskat.dealer import BauernskatDealer
from rlcard.games.bauernskat.round import BauernskatRound
from rlcard.games.bauernskat.game import BauernskatGame

class TestBauernskatGame(unittest.TestCase):
    """
    Tests for BauernskatGame.
    """

    def setUp(self):
        """
        New BauernskatGame for each test.
        """
        self.game = BauernskatGame()

    def test_game_init(self):
        """
        Tests the state after initializing the game.
        """
        
        state, player_id = self.game.init_game()
        
        self.assertEqual(player_id, 0)
        self.assertIn('raw_state_info', state)
        self.assertIn('legal_actions', state)
        self.assertGreater(len(state['raw_state_info']['my_cards']), 0)
        self.assertFalse(self.game.is_over())
    
    def test_game_step_and_transitions(self):
        """
        Tests the step function and the resulting state transitions.
        """
        
        state, _ = self.game.init_game()
        
        declare_action_id = list(state['legal_actions'].keys())[0]
        action_event = ActionEvent.from_action_id(declare_action_id)
        _, next_player_id = self.game.step(action_event)
        
        self.assertEqual(self.game.round.round_phase, 'play')
        self.assertEqual(next_player_id, 0)

        playable_cards = self.game.players[0].get_playable_cards()
        self.assertGreater(len(playable_cards), 0, "Player 0 should have playable cards after trump declaration.")
        card_to_play = playable_cards[0]
        play_action_object = PlayCardAction(card_to_play)
        
        _, final_player_id = self.game.step(play_action_object)
        
        self.assertEqual(final_player_id, 1)
        self.assertEqual(len(self.game.round.trick_moves), 1)

    def _create_deterministic_deck(self, p0_jacks, p1_jacks):
        """
        Helper function to create a deck with specifically placed Jacks.
        """
        
        deck = [None] * 32
        all_cards = set(BauernskatCard.get_deck())

        p0_deal_slots = [31, 30, 29, 28, 23, 22, 21, 20, 15, 14, 13, 12, 7, 6, 5, 4]
        p1_deal_slots = [27, 26, 25, 24, 19, 18, 17, 16, 11, 10, 9, 8, 3, 2, 1, 0]

        for jack in p0_jacks:
            deck[p0_deal_slots.pop()] = jack
            all_cards.remove(jack)
        
        for jack in p1_jacks:
            deck[p1_deal_slots.pop()] = jack
            all_cards.remove(jack)
            
        for i in range(32):
            if deck[i] is None:
                deck[i] = all_cards.pop()
        
        return deck

    def test_get_payoffs_with_matadors(self):
        """
        Tests the original Skat scoring with with different amount of Matadors.
        """
        
        self.game.init_game()
        
        # With 1
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc], p1_jacks=[js, jh, jd])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'H' # Base value = 10
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        # With 1
        self.game.players[0].score = 61
        self.assertEqual(self.game.get_payoffs(), [20.0, -20.0])

        # With 2
        self.game.players[0].score = 60
        self.assertEqual(self.game.get_payoffs(), [-40.0, 40.0])

    def test_get_payoffs_without_matadors(self):
        """
        Tests the original Skat scoring with without x amount of Matadors.
        """
        
        self.game.init_game()

        # Without 2
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jh, jd], p1_jacks=[jc, js])

        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'S'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        # Without 2
        self.game.players[0].score = 70
        self.assertEqual(self.game.get_payoffs(), [33.0, -33.0])

    def test_get_payoffs_grand_game(self):
        """
        Tests the original Skat scoring for a Grand game.
        """
        
        self.game.init_game()
        
        # With 2
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc, js], p1_jacks=[jh, jd])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'G'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        # With 2
        self.game.players[0].score = 80
        self.assertEqual(self.game.get_payoffs(), [72.0, -72.0])
    
    def test_get_payoffs_with_schneider_bonus(self):
        """
        Tests the Schneider multiplier.
        """
        
        self.game.init_game()
        
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc], p1_jacks=[js, jh, jd])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'H'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 91

        self.assertEqual(self.game.get_payoffs(), [40.0, -40.0])
    
    def test_get_payoffs_with_schwarz_bonus(self):
        """
        Tests the Schwarz multiplier.
        """
        
        self.game.init_game()
        
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jh, jd], p1_jacks=[jc, js])

        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'S'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 120

        self.assertEqual(self.game.get_payoffs(), [132.0, -132.0])
    
    def test_get_payoffs_no_schneider_bonus_for_losing_declarer(self):
        """
        Tests for no Schneider or Schwarz multiplier when the declarer loses.
        """
        
        self.game.init_game()
        
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc], p1_jacks=[js, jh, jd])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'H'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 29

        self.assertEqual(self.game.get_payoffs(), [-40.0, 40.0])
    
    def test_get_payoffs_60_60_tie_is_a_loss_for_declarer(self):
        """
        Tests the tie rule where it ends in a loss for the declarer.
        """
        
        self.game.init_game()

        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc], p1_jacks=[js, jh, jd])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'H'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 60

        self.assertEqual(self.game.get_payoffs(), [-40.0, 40.0])
    
    def test_get_payoffs_with_all_matadors(self):
        """
        Tests the scoring for the edge case of having all four Jacks.
        """
        
        self.game.init_game()
        
        # With 4
        jacks = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=jacks, p1_jacks=[])
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'D'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 75

        self.assertEqual(self.game.get_payoffs(), [45.0, -45.0])
    
    def test_get_payoffs_without_any_matadors(self):
        """
        Tests the scoring for the edge case of having none of the four Jacks.
        """
        
        self.game.init_game()
        
        # Without 4
        jacks = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[], p1_jacks=jacks)
        
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'C'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2

        self.game.players[0].score = 65

        self.assertEqual(self.game.get_payoffs(), [60.0, -60.0])
    
    def test_final_state_info(self):
        """
        Tests that pip difference and game value are added to the state when the game ends.
        """
        
        self.game.init_game()
        jc, js, jh, jd = [BauernskatCard(s, 'J') for s in ('C', 'S', 'H', 'D')]
        fixed_deck = self._create_deterministic_deck(p0_jacks=[jc], p1_jacks=[js, jh, jd])
        self.game.round.dealer.shuffled_deck = fixed_deck
        self.game.round.trump_suit = 'H'
        self.game.round.tricks_played = config.NUM_COLUMNS_PER_PLAYER * 2
        self.game.players[0].score = 61
        
        final_state_p0 = self.game.get_state(0)
        final_state_p1 = self.game.get_state(1)

        self.assertIn('pip_difference', final_state_p0['raw_state_info'])
        self.assertIn('game_value_payoff', final_state_p0['raw_state_info'])

        self.assertEqual(final_state_p0['raw_state_info']['pip_difference'], 2) # 61-59
        self.assertEqual(final_state_p0['raw_state_info']['game_value_payoff'], 20.0)

        self.assertEqual(final_state_p1['raw_state_info']['pip_difference'], -2) # 59-61
        self.assertEqual(final_state_p1['raw_state_info']['game_value_payoff'], -20.0)

    def test_get_state_information_levels(self):
        """
        Tests information levels based on the game config.
        """
        
        # "normal" "normal"
        game_normal = BauernskatGame(information_level='normal')
        game_normal.init_game()
        raw_info_normal_p0 = game_normal.get_state(0)['raw_state_info']
        raw_info_normal_p1 = game_normal.get_state(1)['raw_state_info']
        
        self.assertEqual(raw_info_normal_p0['my_hidden_cards'], [])
        self.assertEqual(raw_info_normal_p0['opponent_hidden_cards'], [])
        self.assertEqual(raw_info_normal_p1['my_hidden_cards'], [])
        self.assertEqual(raw_info_normal_p1['opponent_hidden_cards'], [])

        # "show_self" "show_self"
        game_show_self = BauernskatGame(information_level='show_self')
        game_show_self.init_game()
        raw_info_self_p0 = game_show_self.get_state(0)['raw_state_info']
        raw_info_self_p1 = game_show_self.get_state(1)['raw_state_info']

        self.assertGreater(len(raw_info_self_p0['my_hidden_cards']), 0)
        self.assertEqual(len(raw_info_self_p0['opponent_hidden_cards']), 0)
        
        self.assertGreater(len(raw_info_self_p1['my_hidden_cards']), 0)
        self.assertEqual(len(raw_info_self_p1['opponent_hidden_cards']), 0)

        # "perfect" "perfect"
        game_perfect = BauernskatGame(information_level='perfect')
        game_perfect.init_game()
        raw_info_perfect_p0 = game_perfect.get_state(0)['raw_state_info']
        raw_info_perfect_p1 = game_perfect.get_state(1)['raw_state_info']

        self.assertGreater(len(raw_info_perfect_p0['my_hidden_cards']), 0)
        self.assertGreater(len(raw_info_perfect_p0['opponent_hidden_cards']), 0)
        self.assertGreater(len(raw_info_perfect_p1['my_hidden_cards']), 0)
        self.assertGreater(len(raw_info_perfect_p1['opponent_hidden_cards']), 0)

        self.assertEqual(raw_info_perfect_p0['opponent_hidden_cards'], raw_info_perfect_p1['my_hidden_cards'])

        # "perfect" "normal"
        game_mixed = BauernskatGame(information_level={0: 'perfect', 1: 'normal'})
        game_mixed.init_game()
        
        raw_info_mixed_p0 = game_mixed.get_state(0)['raw_state_info']
        raw_info_mixed_p1 = game_mixed.get_state(1)['raw_state_info']

        self.assertGreater(len(raw_info_mixed_p0['my_hidden_cards']), 0)
        self.assertGreater(len(raw_info_mixed_p0['opponent_hidden_cards']), 0)

        self.assertEqual(raw_info_mixed_p1['my_hidden_cards'], [])
        self.assertEqual(raw_info_mixed_p1['opponent_hidden_cards'], [])

    def test_is_over(self):
        """
        Tests the is_over method.
        """
        
        self.game.init_game()
        self.assertFalse(self.game.is_over())
        
        total_tricks = config.NUM_COLUMNS_PER_PLAYER * 2
        self.game.round.tricks_played = total_tricks
        self.assertTrue(self.game.is_over())


if __name__ == '__main__':
    unittest.main()