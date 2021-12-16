'''
    File name: bridge/utils/bridge_card.py
    Author: William Hale
    Date created: 11/25/2021
'''

from rlcard.games.base import Card


class BridgeCard(Card):

    suits = ['C', 'D', 'H', 'S']
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']

    @staticmethod
    def card(card_id: int):
        return _deck[card_id]

    @staticmethod
    def get_deck() -> [Card]:
        return _deck.copy()

    def __init__(self, suit: str, rank: str):
        super().__init__(suit=suit, rank=rank)
        suit_index = BridgeCard.suits.index(self.suit)
        rank_index = BridgeCard.ranks.index(self.rank)
        self.card_id = 13 * suit_index + rank_index

    def __str__(self):
        return f'{self.rank}{self.suit}'

    def __repr__(self):
        return f'{self.rank}{self.suit}'


# deck is always in order from 2C, ... KC, AC, 2D, ... KD, AD, 2H, ... KH, AH, 2S, ... KS, AS
_deck = [BridgeCard(suit=suit, rank=rank) for suit in BridgeCard.suits for rank in BridgeCard.ranks]  # want this to be read-only
