'''
    File name: rlcard/games/bauernskat/player.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

from typing import Optional, List

from . import config
from .card import BauernskatCard


class _CardColumn:
    """
    Helper class to represent a single stack of cards on the table.
    """
    
    def __init__(self) -> None:
        """
        Initializes empty card column.
        """
        
        self.open_card: Optional[BauernskatCard] = None
        self.closed_card: Optional[BauernskatCard] = None

    def is_playable(self) -> bool:
        """
        A column is playable if it has an open card.
        """
        
        return self.open_card is not None

    def has_card_underneath(self) -> bool:
        """
        Checks if playing the open card will reveal a closed card.
        """
        
        return self.closed_card is not None

    def play_card(self) -> BauernskatCard:
        """
        Removes the open card and moves the closed card to the open position.
        """
        
        assert self.is_playable(), "Cannot play a card from an empty column."

        played_card = self.open_card
        self.open_card = self.closed_card
        self.closed_card = None
        
        return played_card

    def __repr__(self) -> str:
        """
        Representation of the card column.
        """
        return f"_CardColumn(open={self.open_card}, closed={self.closed_card is not None})"


class BauernskatPlayer:
    """
    Manages the state of one player in the game.
    """
    
    def __init__(self, player_id: int, np_random) -> None:
        """
        Initializes BauernskatPlayer.
        """
        
        if player_id not in {0, 1}:
            raise ValueError(f"Invalid player_id '{player_id}'. Must be 0 or 1.")

        self.player_id: int = player_id
        self.np_random = np_random
        self.score: int = 0
        self.layout: List[_CardColumn] = [_CardColumn() for _ in range(config.NUM_COLUMNS_PER_PLAYER)]

    def get_playable_cards(self) -> List[BauernskatCard]:
        """
        Returns a list of all cards that are open and can be played.
        """
        
        return [col.open_card for col in self.layout if col.is_playable()]

    def get_hidden_cards(self) -> List[BauernskatCard]:
        """
        Returns a list of all cards that are closed.
        """
        
        return [col.closed_card for col in self.layout if col.has_card_underneath()]

    def find_column_for_card(self, card_to_find: BauernskatCard) -> Optional[_CardColumn]:
        """
        Finds the _CardColumn that currently holds the specific card.
        """
        
        for column in self.layout:
            if column.is_playable() and column.open_card == card_to_find:
                return column
        
        return None
    
    def add_points(self, points: int) -> None:
        """
        Adds points from a won trick to the player score.
        """
        self.score += points

    def __str__(self) -> str:
        """
        String representation of the player.
        """
        return f"Player {self.player_id}"