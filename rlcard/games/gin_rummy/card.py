'''
    File name: gin_rummy/card.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import List


class Card(object):
    '''
    Card stores the card_id, rank and suit of a single card

    Note:
        The card_id lies in range(0, 52)
        The rank variable should be one of [A, 2, 3, 4, 5, 6, 7, 8, 9, T, J, Q, K]
        The suit variable in a gin rummy game should be one of [S, H, D, C] meaning [Spades, Hearts, Diamonds, Clubs]
    '''

    valid_rank = ['A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
    valid_suit = ['S', 'H', 'D', 'C']

    def __init__(self, rank: str, suit: str):
        ''' Initialize the rank, suit, and card_id of a card

        Args:
            rank: string, rank of the card, should be one of valid_rank
            suit: string, suit of the card, should be one of valid_suit
        '''
        assert rank in Card.valid_rank
        assert suit in Card.valid_suit
        self.rank = rank
        self.suit = suit
        self.rank_id = Card.valid_rank.index(rank)
        self.suit_id = Card.valid_suit.index(suit)
        self.card_id = self.rank_id + 13 * self.suit_id

    def __str__(self):
        ''' Get string representation of a card.

        Returns:
            string: the combination of rank and suit of a card. Eg: AS, 5H, JD, 3C, ...
        '''
        return self.rank + self.suit

    def __eq__(self, other):
        if isinstance(other, Card):
            return self.card_id == other.card_id
        else:
            # don't attempt to compare against unrelated types
            return NotImplemented

    def __hash__(self):
        return self.card_id

    @classmethod
    def from_text(cls, text: str):
        assert len(text) == 2
        return Card(rank=text[0], suit=text[1])

    @classmethod
    def from_card_id(cls, card_id: int):
        ''' Make card from its card_id

        Args:
            card_id: int in range(0, 52)
         '''
        assert 0 <= card_id < 52
        rank_id = card_id % 13
        suit_id = card_id // 13
        rank = Card.valid_rank[rank_id]
        suit = Card.valid_suit[suit_id]
        return Card(rank=rank, suit=suit)

    @classmethod
    def init_standard_deck(cls):
        ''' Initialize a standard deck of 52 cards

        Returns:
            (list): A list of Card object
        '''
        return [Card.from_card_id(card_id) for card_id in range(52)]


# deck is always in order from AS, 2S, ..., AH, 2H, ..., AD, 2D, ..., AC, 2C, ... QC, KC
_deck = Card.init_standard_deck()  # want this to be read-only


def get_deck():
    return _deck.copy()


def get_card(card_id: int):
    return _deck[card_id]
