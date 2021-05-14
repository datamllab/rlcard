import unittest
import numpy as np
from rlcard.utils.utils import init_54_deck, init_standard_deck, rank2int, print_card, elegent_form, reorganize, tournament
import rlcard
from rlcard.agents.random_agent import RandomAgent

class TestUtils(unittest.TestCase):

    def test_init_standard_deck(self):
        self.assertEqual(len(init_standard_deck()), 52)

    def test_init_54_deck(self):
        self.assertEqual(len(init_54_deck()), 54)

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

    def test_print_cards(self):
        self.assertEqual(len(elegent_form('S9')), 2)
        self.assertEqual(len(elegent_form('ST')), 3)

        print_card(None)
        print_card('S9')
        print_card('ST')

    def test_reorganize(self):
        trajectories = reorganize([[[1,2],1,[4,5]]], [1])
        self.assertEqual(np.array(trajectories).shape, (1, 1, 5))

    def test_tournament(self):
        env = rlcard.make('leduc-holdem')
        env.set_agents([RandomAgent(env.num_actions), RandomAgent(env.num_actions)])
        payoffs = tournament(env,1000)
        self.assertEqual(len(payoffs), 2)

if __name__ == '__main__':
    unittest.main()
