import unittest
from rlcard.games.limitholdem.utils import compare_hands
from rlcard.games.limitholdem.utils import Hand as Hand
''' Combinations selected for testing compare_hands function
Royal straight flush ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']
Straight flush ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7']
Four of a kind ['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'] ['CT', 'ST', 'HT, 'BT', 'CK', 'C8', 'C7']
Fullhouse ['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'] ['CT', 'ST', 'HT', 'B9', 'C9', 'C8', 'C7'] ['CJ', 'SJ', 'HJ', 'B8', 'C8', 'C5', 'C7']
Flush ['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'] ['CA', 'CQ', 'CT', 'C8', 'C7', 'C4', 'C2']
Straigt ['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'] ['CK', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']
Three of a kind ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'] ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C8', 'C4'] ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'] ['ST', 'ST', 'HT', 'B9', 'C2', 'C8', 'C7']
Two_pairs ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'] ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C5', 'C7'] ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']
One_pair ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'] ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C6'] ['CT', 'ST', 'H9', 'B3', 'C2', 'C8', 'C7']
Highcards ['CJ', 'S5', 'H9', 'B4', 'C2', 'C8', 'C7'] ['CJ', 'S5', 'H9', 'B4', 'C3', 'C8', 'C7']
'''
class TestHoldemUtils(unittest.TestCase):

    def test_evaluate_hand_exception(self):

        hand = Hand(['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8'])
        with self.assertRaises(Exception):
            hand.evaluateHand()

    def test_has_high_card_false(self):

        hand = Hand(['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'S3'])
        hand.product = 20
        self.assertEqual(hand._has_high_card(), False)

    def test_compare_hands(self):

        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CQ', 'SQ', 'H9', 'B3', 'C2', 'C8', 'C6']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7'], None])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [None, ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1])
        #straight flush
        hands1 = [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'],
        ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7'],
        ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7'],
        ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7'],
        ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7']]
        winner = compare_hands(hands1)
        self.assertEqual(winner, [0, 1, 1, 1, 1])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'],
        ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1, 0])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'],
        ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7'], None])
        self.assertEqual(winner, [0, 1, 0, 0])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 1])
        #Compare between different catagories
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'], ['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7'], ['HJ', 'S5', 'C9', 'B3', 'H2', 'H8', 'H7']])
        self.assertEqual(winner, [1, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        hands2 = [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'],
        ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'],
        ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA'],
        ['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']]
        winner = compare_hands(hands2)
        self.assertEqual(winner, [0, 1, 1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CJ', 'CT', 'CQ', 'CK', 'C9', 'C8', 'CA']])
        self.assertEqual(winner, [0, 1])
        #Four of a kind
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'BJ', 'C8', 'C3', 'C4']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C3', 'C4']])
        self.assertEqual(winner, [1, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        #Fullhouse
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CT', 'ST', 'HT', 'B9', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C6']])
        self.assertEqual(winner, [1, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B5', 'C5', 'C8', 'C6']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'BT', 'CT', 'C8', 'C6']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B8', 'C8', 'C7', 'C6']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        #Flush
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        #Straight
        winner = compare_hands( [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        #Two pairs
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CT', 'ST', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CT', 'ST', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'],
        ['CT', 'ST', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7'],
        ['CJ', 'SJ', 'HT', 'BT', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C5', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C5']])
        self.assertEqual(winner, [1, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CJ', 'S5', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'BJ', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'BJ', 'CT', 'B8', 'C7']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CT', 'ST', 'HT', 'B9', 'C9', 'C8', 'C7'], ['CJ', 'SJ', 'HJ', 'B9', 'C9', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'S5', 'H9', 'B4', 'C2', 'C8', 'C7'], ['CJ', 'S6', 'H9', 'B4', 'C3', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CA', 'CQ', 'CT', 'C8', 'C6', 'C4', 'C2'], ['CA', 'CQ', 'CT', 'C8', 'C7', 'C4', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7'], ['CK', 'ST', 'HQ', 'BK', 'B9', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C7'], ['ST', 'ST', 'HT', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        #Three of a kind
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CQ', 'SQ', 'HQ', 'B9', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'BT', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'B7', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C6', 'C4']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C6', 'C4']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C7', 'C4'], ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H6', 'B6', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B9', 'C2', 'C5', 'C7'], ['CJ', 'SJ', 'H9', 'B9', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HJ', 'B9', 'C2', 'C8', 'C4'], ['CJ', 'SJ', 'HJ', 'B9', 'C3', 'C8', 'C4']])
        self.assertEqual(winner, [1, 1])
        #One pair
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CT', 'ST', 'H9', 'B3', 'C2', 'C8', 'C7']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C6']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'B3', 'C2', 'C8', 'C7'], ['CQ', 'SQ', 'H9', 'B3', 'C2', 'C8', 'C6']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'HT', 'C8', 'C7', 'B3', 'C2'], ['CJ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CJ', 'SJ', 'HT', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CJ', 'SJ', 'HT', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CJ', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2'], ['CJ', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2'], ['CJ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CJ', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2'], ['CJ', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 1])
        #high_cards
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2'], ['CQ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CQ', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CK', 'SQ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C8', 'C6', 'B3', 'C2'], ['CK', 'SQ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CK', 'SJ', 'H8', 'C7', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CK', 'SJ', 'H8', 'C7', 'C6', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C8', 'C7', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C7', 'C5', 'B3', 'C2']])
        self.assertEqual(winner, [1, 0])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C7', 'C5', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [0, 1])
        winner = compare_hands( [['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2'], ['CK', 'SJ', 'H9', 'C7', 'C6', 'B3', 'C2']])
        self.assertEqual(winner, [1, 1])
        winner = compare_hands([['C5', 'S9', 'S6', 'C2', 'CT', 'C7', 'H5'], ['S7', 'SJ', 'S6', 'C2', 'CT', 'C7', 'H5'], None, None, ['H7', 'DJ', 'S6', 'C2', 'CT', 'C7', 'H5'], None])
        self.assertEqual(winner, [0, 1, 0, 0, 1, 0])

        winner = compare_hands([['H3', 'D5', 'S6', 'H9', 'CA', 'HA', 'SA'],   # three of a kind
                                ['H2', 'H3', 'C4', 'D5', 'C6', 'S6', 'ST']])  # straight
        self.assertEqual(winner, [0, 1])

        winner = compare_hands([['H3', 'D5', 'S6', 'H9', 'CA', 'HA', 'SA'],   # three of a kind
                                ['H2', 'H3', 'C4', 'D5', 'CQ', 'SK', 'SA']])  # straight beginning with A
        self.assertEqual(winner, [0, 1])

        winner = compare_hands([['H5', 'HQ', 'C2', 'D3', 'S4', 'S5', 'HT'],   # pair
                                ['D5', 'ST', 'C2', 'D3', 'S4', 'S5', 'HA'],   # A,2,3,4,5
                                ['H6', 'HQ', 'C2', 'D3', 'S4', 'S5', 'HT'],   # 2,3,4,5,6
                                ['H4', 'HQ', 'C2', 'D3', 'S4', 'S5', 'HT'],   # pair
                                ])
        self.assertEqual(winner, [0, 0, 1, 0])

        winner = compare_hands([['D5', 'ST', 'C2', 'D3', 'S4', 'S5', 'HA'],   # A,2,3,4,5
                                ['H6', 'H7', 'CK', 'DQ', 'SJ', 'ST', 'HA'],   # T,J,Q,K,A
                                ['HA', 'HT', 'CK', 'DQ', 'SJ', 'ST', 'DT'],   # T,J,Q,K,A
                                ['H2', 'H3', 'C4', 'D2', 'CQ', 'S2', 'SA'],   # three of a kind
                                ])
        self.assertEqual(winner, [0, 1, 1, 0])

        winner = compare_hands([['H5', 'HQ', 'C2', 'D3', 'S4', 'S5', 'HT'],   # pair
                                ['D5', 'ST', 'S2', 'S3', 'S4', 'S5', 'SA'],   # A,2,3,4,5 suited
                                ['C6', 'HQ', 'C2', 'C3', 'C4', 'C5', 'HT'],   # 2,3,4,5,6 suited
                                ['H7', 'H6', 'C9', 'C3', 'C4', 'C5', 'HT'],   # 3,4,5,6,7 not suited
                                ])
        self.assertEqual(winner, [0, 0, 1, 0])
     
        winner = compare_hands([['S2', 'D8', 'H8', 'S7', 'S8', 'C8', 'D3'],  # 8-four of a kind, kicker 7
                                ['S2', 'D8', 'H8', 'S9', 'S8', 'C8', 'D3'],  # 8-four of a kind, kicker 9
                                ['H3', 'C3', 'HT', 'S3', 'ST', 'CT', 'D3'],  # 3-four of a kind, kicker T
                                ])
        self.assertEqual(winner, [0, 1, 0])

        winner = compare_hands([['CA', 'C2', 'DJ', 'CT', 'S7', 'C5', 'ST'],  # pair T, T, kicker A, J
                                ['S3', 'S4', 'DJ', 'CT', 'S7', 'C5', 'ST'],  # pair T, T, kicker J, 4
                                ['HQ', 'DA', 'DJ', 'CT', 'S7', 'C5', 'ST'],  # pair T, T, kicker A, Q
                                ['SQ', 'HA', 'DJ', 'CT', 'S7', 'C5', 'ST']   # pair T, T, kicker A, Q
                                ])
        self.assertEqual(winner, [0, 0, 1, 1])


if __name__ == '__main__':
    unittest.main()
