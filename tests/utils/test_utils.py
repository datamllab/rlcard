import unittest
import numpy as np
from rlcard.utils.utils import get_random_cards, init_54_deck, init_standard_deck, is_in_cards, is_pair, is_single, rank2int, take_out_cards, print_card, elegent_form, init_players, get_upstream_player_id, get_downstream_player_id, reorganize, set_global_seed, get_cards_from_ranks,tournament
import rlcard
from rlcard.agents.random_agent import RandomAgent

from rlcard.core import Card, Player

class TestUtils(unittest.TestCase):

    def test_init_standard_deck(self):
        self.assertEqual(len(init_standard_deck()), 52)

    def test_init_54_deck(self):
        self.assertEqual(len(init_54_deck()), 54)

    def test_get_random_cards(self):
        hand = init_54_deck()
        num = 10
        chosen_cards, remained_cards = get_random_cards(hand, num)
        self.assertEqual(len(chosen_cards), num)
        self.assertEqual(len(remained_cards), len(hand) - num)
        with self.assertRaises(AssertionError):
            get_random_cards(hand, 1000)
        with self.assertRaises(AssertionError):
            get_random_cards(hand, -1)


    def test_is_pair(self):
        self.assertTrue(is_pair([Card('S', 'A'), Card('D', 'A')]))
        self.assertFalse(is_pair([Card('BJ', ''), Card('S', 'A'), Card('D', 'A')]))

    def test_is_single(self):
        self.assertTrue(is_single([Card('S', 'A')]))
        self.assertFalse(is_single([Card('S', 'A'), Card('BJ', '')]))

    def test_rank2int(self):
        self.assertEqual(rank2int('A'), 14)
        self.assertEqual(rank2int(''), -1)
        self.assertEqual(rank2int('3'), 3)
        self.assertEqual(rank2int('T'), 10)
        self.assertEqual(rank2int('J'), 11)
        self.assertEqual(rank2int('Q'), 12)
        self.assertEqual(rank2int('1000'), None)
        self.assertEqual(rank2int('abc123'), None)
        self.assertEqual(rank2int('K'), 13)

    def test_get_cards_from_ranks(self):
        deck = init_54_deck()
        player = Player(0)
        player.hand = deck
        test_ranks = ['A', '2', '3']
        chosen_cards, remained_cards = get_cards_from_ranks(player, test_ranks)
        self.assertEqual(len(chosen_cards), 12)
        for card in chosen_cards:
            flag = True
            if card.rank in test_ranks:
                flag = False
            self.assertFalse(flag)
        self.assertEqual(len(remained_cards), len(deck) - 12)
        self.assertEqual(len(chosen_cards), 12)

    def test_take_out_cards(self):
        cards = init_54_deck()
        remove_cards = [Card('S', 'A'), Card('BJ', '')]
        res = take_out_cards(cards, remove_cards)
        flag = False
        for card in res:
            if card.get_index() == 'SA' or card.get_index == 'BJ':
                flag = True
        self.assertFalse(flag)
        self.assertEqual(len(cards), len(init_54_deck()) - 2)

    def test_is_in_cards(self):
        deck54 = init_54_deck()
        deck_standard = init_standard_deck()
        deck54_plus_BJ = init_54_deck()
        deck54_plus_BJ.append(Card('BJ', ''))
        self.assertTrue(is_in_cards(deck54, deck_standard))
        self.assertTrue(is_in_cards(deck54, [Card('BJ', ''), Card('RJ', '')]))
        self.assertFalse(is_in_cards(deck54, [Card('BJ', ''), Card('BJ', '')]))
        self.assertFalse(is_in_cards(deck54, [Card('BJ', ''), Card('BJ', ''), Card('D', '3')]))
        self.assertTrue(is_in_cards(deck54_plus_BJ, [Card('BJ', ''), Card('BJ', ''), Card('D', '3')]))

    def test_print_cards(self):
        self.assertEqual(len(elegent_form('S9')), 2)
        self.assertEqual(len(elegent_form('ST')), 3)

        print_card(None)
        print_card('S9')
        print_card('ST')

    def test_init_players(self):
        self.assertTrue(len(init_players(5)), 5)

    def test_get_upstream_player_id(self):
        players = init_players(5)
        self.assertEqual(get_upstream_player_id(players[0], players), 4)

    def test_get_downstream_player_id(self):
        players = init_players(5)
        self.assertEqual(get_downstream_player_id(players[4], players), 0)

    def test_reorganize(self):
        trajectories = reorganize([[[1,2],1,[4,5]]], [1])
        self.assertEqual(np.array(trajectories).shape, (1, 1, 5))

    def test_set_global_seed(self):
        set_global_seed(0)
        self.assertEqual(np.random.get_state()[1][0], 0)

    def test_tournament(self):
        env = rlcard.make('leduc-holdem')
        env.set_agents([RandomAgent(env.action_num), RandomAgent(env.action_num)])
        payoffs = tournament(env,1000)
        self.assertEqual(len(payoffs), 2)



if __name__ == '__main__':
    unittest.main()
