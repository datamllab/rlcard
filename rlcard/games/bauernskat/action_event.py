'''
    File name: rlcard/games/bauernskat/action_event.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

from . import config
from .card import BauernskatCard


class ActionEvent:
    """
    A base class for actions that can occur in Bauernskat.
    """

    def __init__(self, action_id: int) -> None:
        """
        Initializes ActionEvent.
        """
        self.action_id: int = action_id

    def __eq__(self, other: object) -> bool:
        """
        Equality check based on action_id.
        """
        if not isinstance(other, ActionEvent):
            return NotImplemented
        return self.action_id == other.action_id
    
    def __hash__(self) -> int:
        """
        Hash based on action ID.
        """
        return hash(self.action_id)

    @staticmethod
    def from_action_id(action_id: int) -> 'ActionEvent':
        """
        Creates an action event based on its ID.
        """
        if config.FIRST_DECLARE_TRUMP_ACTION_ID <= action_id < config.FIRST_PLAY_CARD_ACTION_ID:
            return DeclareTrumpAction.from_action_id(action_id)

        if config.FIRST_PLAY_CARD_ACTION_ID <= action_id < config.TOTAL_NUM_ACTIONS:
            card_id = action_id - config.FIRST_PLAY_CARD_ACTION_ID
            card = BauernskatCard.card(card_id=card_id)
            return PlayCardAction(card=card)

        raise ValueError(f"Invalid action_id {action_id}. Must be between 0 and {config.TOTAL_NUM_ACTIONS - 1}.")

    @staticmethod
    def get_num_actions() -> int:
        """
        Returns the number of possible actions.
        """
        return config.TOTAL_NUM_ACTIONS


class DeclareTrumpAction(ActionEvent):
    """
    ActionEvent for declaring a trump suit or a grand.
    """
    
    VALID_TRUMPS: tuple[str, ...] = BauernskatCard.suits + ('G',)

    def __init__(self, trump_suit: str) -> None:
        """
        Initializes DeclareTrumpAction.
        """
        
        if trump_suit not in self.VALID_TRUMPS:
            raise ValueError(f"Invalid trump suit '{trump_suit}'. Must be one of {self.VALID_TRUMPS}.")

        self.trump_suit: str = trump_suit
        action_id = config.FIRST_DECLARE_TRUMP_ACTION_ID + self.VALID_TRUMPS.index(trump_suit)
        
        super().__init__(action_id)

    @classmethod
    def from_action_id(cls, action_id: int) -> 'DeclareTrumpAction':
        """
        Creates a DeclareTrumpAction from the ID.
        """
        
        trump_index = action_id - config.FIRST_DECLARE_TRUMP_ACTION_ID
        trump_suit = cls.VALID_TRUMPS[trump_index]
        
        return cls(trump_suit)

    def __str__(self) -> str:
        """
        String representation of a DeclareTrumpAction.
        """
        return f"Declare {self.trump_suit}"

    def __repr__(self) -> str:
        """
        Representation of a DeclareTrumpAction object.
        """
        return f"DeclareTrumpAction(trump_suit='{self.trump_suit}')"


class PlayCardAction(ActionEvent):
    """
    ActionEvent for playing a card.
    """
    
    def __init__(self, card: BauernskatCard) -> None:
        """
        Initializes PlayCardAction.
        """
        
        self.card: BauernskatCard = card
        action_id = config.FIRST_PLAY_CARD_ACTION_ID + card.card_id
        
        super().__init__(action_id)

    def __str__(self) -> str:
        """
        String representation of a PlayCardAction.
        """
        return f"Play {self.card}"

    def __repr__(self) -> str:
        """
        Representation of a PlayCardAction object.
        """
        return f"PlayCardAction(card={repr(self.card)})"