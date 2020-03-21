'''
    File name: test_gin_rummy_game.py
    Author: William Hale
    Date created: 3/11/2020
'''

import unittest
import numpy as np

from rlcard.games.gin_rummy.dealer import GinRummyDealer
from rlcard.games.gin_rummy.game import GinRummyGame as Game
from rlcard.games.gin_rummy.player import GinRummyPlayer
from rlcard.games.gin_rummy.utils.action_event import score_player_1_action_id
from rlcard.games.gin_rummy.utils.action_event import draw_card_action_id, pick_up_discard_action_id
from rlcard.games.gin_rummy.utils.action_event import declare_dead_hand_action_id
from rlcard.games.gin_rummy.utils.action_event import gin_action_id, discard_action_id, knock_action_id

from rlcard.games.gin_rummy.card import Card, get_deck

from rlcard.games.gin_rummy.utils.melding import _get_all_set_melds, _get_all_run_melds, get_meld_clusters
from rlcard.games.gin_rummy.utils.settings import Setting, Settings

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
        _, current_player = game.init_game()
        opponent_player = (current_player + 1) % 2
        action = np.random.choice(game.judge.get_legal_actions())
        self.assertIn(action.action_id, put_action_ids)  # should be a put action
        next_state, next_player = game.step(action)
        if not game.is_over():
            self.assertEqual(next_player, opponent_player)
        if not game.is_over():
            action = np.random.choice(game.judge.get_legal_actions())
            self.assertIn(action.action_id, get_action_ids)  # should be a get action
            next_state, next_player = game.step(action)
            self.assertEqual(next_player, opponent_player)  # keep turn to put card

    def test_proceed_game(self):
        game = Game()
        game.init_game()
        while not game.is_over():
            legal_actions = game.judge.get_legal_actions()
            action = np.random.choice(legal_actions)
            state, _ = game.step(action)
        self.assertEqual(game.actions[-1].action_id, score_player_1_action_id)

    def test_get_state(self):
        game = Game()
        state, current_player = game.init_game()
        self.assertEqual(len(state), 6)

    def test_gin_rummy_dealer(self):
        dealer = GinRummyDealer()
        current_deck = get_deck()
        deck_card_ids = [card.card_id for card in current_deck]
        self.assertEqual(deck_card_ids, list(range(52)))
        # Deal 10 cards.
        player = GinRummyPlayer(player_id=0)
        dealer.deal_cards(player=player, num=10)
        self.assertEqual(len(dealer.shuffled_deck), 52)
        self.assertEqual(len(dealer.stock_pile), 42)
        self.assertEqual(len(current_deck), 52)
        self.assertEqual(len(get_deck()), 52)
        # Pop top_card from current_deck.
        top_card = current_deck.pop(-1)
        self.assertEqual(str(top_card), "KC")
        self.assertEqual(len(current_deck), 51)
        self.assertEqual(len(get_deck()), 52)

    def test_melding(self):
        hand_text = ['9H', 'AC', 'TH', '3C', '3D', '7C', 'QH', '3H', '8C', '8D',
                     '4D', '7H', '8S', '5H', '4H', 'AS', 'TD', '3S', '2S', 'AH']
        hand = [Card.from_text(x) for x in hand_text]

        # check
        all_set_melds_text = [['3C', '3D', '3H', '3S'], ['8C', '8D', '8S'], ['AC', 'AS', 'AH'], ['3D', '3H', '3S'],
                              ['3C', '3H', '3S'], ['3C', '3D', '3S'], ['3C', '3D', '3H']]
        all_set_melds = _get_all_set_melds(hand)
        self.assertEqual(all_set_melds_text, [[str(card) for card in meld_pile] for meld_pile in all_set_melds])

        # check
        all_run_melds_text = [['AS', '2S', '3S'], ['3H', '4H', '5H']]
        all_run_melds = _get_all_run_melds(hand)
        self.assertEqual(all_run_melds_text, [[str(card) for card in meld_pile] for meld_pile in all_run_melds])

        # check
        meld_clusters = get_meld_clusters(hand=hand)
        self.assertEqual(len(meld_clusters), 36)

    def test_corrected_settings(self):
        default_setting = Setting.default_setting()
        config = {Setting.max_drawn_card_count: 10,
                  Setting.stockpile_dead_card_count: 4.5,
                  Setting.is_allowed_pick_up_discard: 0}
        corrected_config = Settings.get_config_with_invalid_settings_set_to_default_value(config=config)
        self.assertEqual(corrected_config[Setting.max_drawn_card_count], 10)
        self.assertEqual(corrected_config[Setting.stockpile_dead_card_count],
                         default_setting[Setting.stockpile_dead_card_count])
        self.assertEqual(corrected_config[Setting.is_allowed_pick_up_discard],
                         default_setting[Setting.is_allowed_pick_up_discard])

    def test_change_settings(self):
        default_setting = Setting.default_setting()
        config = {Setting.max_drawn_card_count: 10,
                  Setting.stockpile_dead_card_count: 4.5,
                  Setting.is_allowed_pick_up_discard: 0}
        settings = Settings()
        settings.change_settings(config=config)
        self.assertEqual(settings.max_drawn_card_count, 10)
        self.assertEqual(settings.stockpile_dead_card_count,
                         default_setting[Setting.stockpile_dead_card_count])
        self.assertEqual(settings.is_allowed_pick_up_discard,
                         default_setting[Setting.is_allowed_pick_up_discard])


if __name__ == '__main__':
    unittest.main()
