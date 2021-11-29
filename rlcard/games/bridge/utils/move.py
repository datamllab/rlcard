'''
    File name: bridge/utils/move.py
    Author: William Hale
    Date created: 11/25/2021
'''

#
#   These classes are used to keep a move_sheet history of the moves in a round.
#

from .action_event import ActionEvent, BidAction, PassAction, DblAction, RdblAction, PlayCardAction
from .bridge_card import BridgeCard

from ..player import BridgePlayer


class BridgeMove(object):  # Interface
    pass


class PlayerMove(BridgeMove):  # Interface

    def __init__(self, player: BridgePlayer, action: ActionEvent):
        super().__init__()
        self.player = player
        self.action = action


class CallMove(PlayerMove):  # Interface

    def __init__(self, player: BridgePlayer, action: ActionEvent):
        super().__init__(player=player, action=action)


class DealHandMove(BridgeMove):

    def __init__(self, dealer: BridgePlayer, shuffled_deck: [BridgeCard]):
        super().__init__()
        self.dealer = dealer
        self.shuffled_deck = shuffled_deck

    def __str__(self):
        shuffled_deck_text = " ".join([str(card) for card in self.shuffled_deck])
        return f'{self.dealer} deal shuffled_deck=[{shuffled_deck_text}]'


class MakePassMove(CallMove):

    def __init__(self, player: BridgePlayer):
        super().__init__(player=player, action=PassAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeDblMove(CallMove):

    def __init__(self, player: BridgePlayer):
        super().__init__(player=player, action=DblAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeRdblMove(CallMove):

    def __init__(self, player: BridgePlayer):
        super().__init__(player=player, action=RdblAction())

    def __str__(self):
        return f'{self.player} {self.action}'


class MakeBidMove(CallMove):

    def __init__(self, player: BridgePlayer, bid_action: BidAction):
        super().__init__(player=player, action=bid_action)
        self.action = bid_action  # Note: keep type as BidAction rather than ActionEvent

    def __str__(self):
        return f'{self.player} bids {self.action}'


class PlayCardMove(PlayerMove):

    def __init__(self, player: BridgePlayer, action: PlayCardAction):
        super().__init__(player=player, action=action)
        self.action = action  # Note: keep type as PlayCardAction rather than ActionEvent

    @property
    def card(self):
        return self.action.card

    def __str__(self):
        return f'{self.player} plays {self.action}'
