'''
    File name: bridge/utils/action_event.py
    Author: William Hale
    Date created: 11/25/2021
'''

from .bridge_card import BridgeCard

# ====================================
# Action_ids:
#       0 -> no_bid_action_id
#       1 to 35 -> bid_action_id (bid amount by suit or NT)
#       36 -> pass_action_id
#       37 -> dbl_action_id
#       38 -> rdbl_action_id
#       39 to 90 -> play_card_action_id
# ====================================


class ActionEvent(object):  # Interface

    no_bid_action_id = 0
    first_bid_action_id = 1
    pass_action_id = 36
    dbl_action_id = 37
    rdbl_action_id = 38
    first_play_card_action_id = 39

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def from_action_id(action_id: int):
        if action_id == ActionEvent.pass_action_id:
            return PassAction()
        elif ActionEvent.first_bid_action_id <= action_id <= 35:
            bid_amount = 1 + (action_id - ActionEvent.first_bid_action_id) // 5
            bid_suit_id = (action_id - ActionEvent.first_bid_action_id) % 5
            bid_suit = BridgeCard.suits[bid_suit_id] if bid_suit_id < 4 else None
            return BidAction(bid_amount, bid_suit)
        elif action_id == ActionEvent.dbl_action_id:
            return DblAction()
        elif action_id == ActionEvent.rdbl_action_id:
            return RdblAction()
        elif ActionEvent.first_play_card_action_id <= action_id < ActionEvent.first_play_card_action_id + 52:
            card_id = action_id - ActionEvent.first_play_card_action_id
            card = BridgeCard.card(card_id=card_id)
            return PlayCardAction(card=card)
        else:
            raise Exception(f'ActionEvent from_action_id: invalid action_id={action_id}')

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return 1 + 35 + 3 + 52  # no_bid, 35 bids, pass, dbl, rdl, 52 play_card


class CallActionEvent(ActionEvent):  # Interface
    pass


class PassAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.pass_action_id)

    def __str__(self):
        return "pass"

    def __repr__(self):
        return "pass"


class BidAction(CallActionEvent):

    def __init__(self, bid_amount: int, bid_suit: str or None):
        suits = BridgeCard.suits
        if bid_suit and bid_suit not in suits:
            raise Exception(f'BidAction has invalid suit: {bid_suit}')
        if bid_suit in suits:
            bid_suit_id = suits.index(bid_suit)
        else:
            bid_suit_id = 4
        bid_action_id = bid_suit_id + 5 * (bid_amount - 1) + ActionEvent.first_bid_action_id
        super().__init__(action_id=bid_action_id)
        self.bid_amount = bid_amount
        self.bid_suit = bid_suit

    def __str__(self):
        bid_suit = self.bid_suit
        if not bid_suit:
            bid_suit = 'NT'
        return f'{self.bid_amount}{bid_suit}'

    def __repr__(self):
        return self.__str__()


class DblAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.dbl_action_id)

    def __str__(self):
        return "dbl"

    def __repr__(self):
        return "dbl"


class RdblAction(CallActionEvent):

    def __init__(self):
        super().__init__(action_id=ActionEvent.rdbl_action_id)

    def __str__(self):
        return "rdbl"

    def __repr__(self):
        return "rdbl"


class PlayCardAction(ActionEvent):

    def __init__(self, card: BridgeCard):
        play_card_action_id = ActionEvent.first_play_card_action_id + card.card_id
        super().__init__(action_id=play_card_action_id)
        self.card: BridgeCard = card

    def __str__(self):
        return f"{self.card}"

    def __repr__(self):
        return f"{self.card}"
