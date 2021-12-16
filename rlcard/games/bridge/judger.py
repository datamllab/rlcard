'''
    File name: bridge/judger.py
    Author: William Hale
    Date created: 11/25/2021
'''

from typing import List

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game import BridgeGame

from .utils.action_event import PlayCardAction
from .utils.action_event import ActionEvent, BidAction, PassAction, DblAction, RdblAction
from .utils.move import MakeBidMove, MakeDblMove, MakeRdblMove
from .utils.bridge_card import BridgeCard


class BridgeJudger:

    '''
        Judger decides legal actions for current player
    '''

    def __init__(self, game: 'BridgeGame'):
        ''' Initialize the class BridgeJudger
        :param game: BridgeGame
        '''
        self.game: BridgeGame = game

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions: List[ActionEvent] = []
        if not self.game.is_over():
            current_player = self.game.round.get_current_player()
            if not self.game.round.is_bidding_over():
                legal_actions.append(PassAction())
                last_make_bid_move: MakeBidMove or None = None
                last_dbl_move: MakeDblMove or None = None
                last_rdbl_move: MakeRdblMove or None = None
                for move in reversed(self.game.round.move_sheet):
                    if isinstance(move, MakeBidMove):
                        last_make_bid_move = move
                        break
                    elif isinstance(move, MakeRdblMove):
                        last_rdbl_move = move
                    elif isinstance(move, MakeDblMove) and not last_rdbl_move:
                        last_dbl_move = move
                first_bid_action_id = ActionEvent.first_bid_action_id
                next_bid_action_id = last_make_bid_move.action.action_id + 1 if last_make_bid_move else first_bid_action_id
                for bid_action_id in range(next_bid_action_id, first_bid_action_id + 35):
                    action = BidAction.from_action_id(action_id=bid_action_id)
                    legal_actions.append(action)
                if last_make_bid_move and last_make_bid_move.player.player_id % 2 != current_player.player_id % 2 and not last_dbl_move and not last_rdbl_move:
                    legal_actions.append(DblAction())
                if last_dbl_move and last_dbl_move.player.player_id % 2 != current_player.player_id % 2:
                    legal_actions.append(RdblAction())
            else:
                trick_moves = self.game.round.get_trick_moves()
                hand = self.game.round.players[current_player.player_id].hand
                legal_cards = hand
                if trick_moves and len(trick_moves) < 4:
                    led_card: BridgeCard = trick_moves[0].card
                    cards_of_led_suit = [card for card in hand if card.suit == led_card.suit]
                    if cards_of_led_suit:
                        legal_cards = cards_of_led_suit
                for card in legal_cards:
                    action = PlayCardAction(card=card)
                    legal_actions.append(action)
        return legal_actions
