'''
    File name: rlcard/games/bauernskat/card.py
    Author: Oliver Czerwinski
    Date created: 17/07/2025
    Date last modified: 25/12/2025
    Python Version: 3.9+
'''

from . import config
from rlcard.games.base import Card


class BauernskatCard(Card):
    """
    BauernskatCard implements the properties of a card in a 32-card Skat deck.
    """

    suits: tuple[str, ...] = config.VALID_SUITS
    ranks: tuple[str, ...] = config.VALID_RANKS

    def __init__(self, suit: str, rank: str) -> None:
        """
        Initializes a BauernskatCard.
        """
        super().__init__(suit, rank)

        if suit not in self.suits:
            raise ValueError(f"Invalid suit '{suit}'. Must be one of {self.suits}.")
        if rank not in self.ranks:
            raise ValueError(f"Invalid rank '{rank}'. Must be one of {self.ranks}.")

        # Calculate IDs for all combinations
        suit_index: int = self.suits.index(suit)
        rank_index: int = self.ranks.index(rank)
        self.card_id: int = suit_index * len(self.ranks) + rank_index

        self.points: int = config.RANK_VALUES[self.rank]

    def __str__(self) -> str:
        """
        String representation of a card.
        """
        return f'{self.rank}{self.suit}'

    def __repr__(self) -> str:
        """
        Representation of card object.
        """
        return f"BauernskatCard('{self.suit}', '{self.rank}')"
    
    def __eq__(self, other: object) -> bool:
        """
        Equality check based on card ID.
        """
        if not isinstance(other, BauernskatCard):
            return NotImplemented
        return self.card_id == other.card_id

    def __hash__(self) -> int:
        """
        Hash based on card ID.
        """
        return hash(self.card_id)

    @staticmethod
    def card(card_id: int) -> 'BauernskatCard':
        """
        Gets a valid card instance from the deck using the ID.
        """
        if not 0 <= card_id < len(_DECK):
            raise IndexError(f"card_id {card_id} is out of range. Must be between 0 and 31.")
        return _DECK[card_id]

    @staticmethod
    def get_deck() -> list['BauernskatCard']:
        """
        Returns a copy of the 32-card deck.
        """
        return _DECK.copy()


# Source deck to only generate once
_DECK: list[BauernskatCard] = [BauernskatCard(suit, rank) for suit in config.VALID_SUITS for rank in config.VALID_RANKS]