'''
    File name: rlcard/games/bauernskat/judger.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
    Python Version: 3.9+
'''

from typing import List, TYPE_CHECKING

from .action_event import ActionEvent, DeclareTrumpAction, PlayCardAction
from .card import BauernskatCard

if TYPE_CHECKING:
    from .game import BauernskatGame


class BauernskatJudger:
    """
    Determines the set of legal actions for a player at any point of time.
    """

    def __init__(self, game: 'BauernskatGame') -> None:
        """
        Initializes BauernskatJudger.
        """
        
        self.game: 'BauernskatGame' = game

    def _is_trump(self, card: BauernskatCard, trump_suit: str) -> bool:
        """
        Determines if a card is a trump card in the game.
        - Grand: Only Jacks.
        - Color Suit: All Jacks and all cards of the selected suit.
        """
        
        assert trump_suit is not None, "Trump suit must be declared to check for trumps."

        if trump_suit == 'G':
            return card.rank == 'J'

        if card.rank == 'J':
            return True
        
        if card.suit == trump_suit:
            return True

        return False

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        List of legal actions for the current player.
        """
        
        round = self.game.round
        
        if round.is_over():
            return []

        if round.round_phase == 'declare_trump':
            return [DeclareTrumpAction(suit) for suit in DeclareTrumpAction.VALID_TRUMPS]

        if round.round_phase == 'play':
            current_player = round.players[round.current_player_id]
            playable_cards = current_player.get_playable_cards()

            if not playable_cards:
                return []

            # Player is starting the trick: Any card is legal
            if not round.trick_moves:
                return [PlayCardAction(card) for card in playable_cards]

            # Player is answering the trick: Must play specific suit/trump if possible
            led_card = round.trick_moves[0][1]
            trump_suit = round.trump_suit

            # A trump card has been played: Player must answer a trump card if possible
            if self._is_trump(led_card, trump_suit):
                trumps_in_hand = [card for card in playable_cards if self._is_trump(card, trump_suit)]
                if trumps_in_hand:
                    return [PlayCardAction(card) for card in trumps_in_hand]
            
            # A non-trump card has been played: Player must answer with that suit if possible
            else:
                led_suit = led_card.suit
                
                suit_in_hand = [card for card in playable_cards if card.suit == led_suit and not self._is_trump(card, trump_suit)]
                if suit_in_hand:
                    return [PlayCardAction(card) for card in suit_in_hand]

            # If the player has no fitting cards, they can answer with any other card
            return [PlayCardAction(card) for card in playable_cards]
        
        return []