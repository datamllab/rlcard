import sys
from os import path
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from functools import reduce
import random
from core import Card

def init_standard_deck():
    ''' Return a list of Card objects which form a standard 52 cards deck
    '''
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    return res

def init_54_deck():
    ''' Return a list of Card objects which include a standard 52 cards deck, BJ and RJ
    '''
    suit_list = ['S', 'H', 'D', 'C']
    rank_list = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
    res = [Card(suit, rank) for suit in suit_list for rank in rank_list]
    res.append(Card('BJ', ''))
    res.append(Card('RJ', ''))
    return res

def get_random_cards(cards, num, seed = None):
    ''' Randomly get a number of chosen cards out of a list of cards

    Args:
        cards: list of Card object
        num: int, number of cards to be chosen
        seed: int, optional, random seed

    Return:
        list: list of chosen cards
        list: list of remained cards
    '''
    assert num > 0, "Invalid input number"
    assert num <= len(cards), "Input number larger than length of cards"
    remained_cards = []
    chosen_cards = []
    remained_cards = cards.copy()
    random.Random(seed).shuffle(remained_cards)
    chosen_cards = remained_cards[:num]
    remained_cards = remained_cards[num:]
    return chosen_cards, remained_cards
