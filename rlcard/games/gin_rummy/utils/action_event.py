'''
    File name: gin_rummy/action_event.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.base import Card

from . import utils as utils

# ====================================
# Action_ids:
#        0 -> score_player_0_id
#        1 -> score_player_1_id
#        2 -> draw_card_id
#        3 -> pick_up_discard_id
#        4 -> declare_dead_hand_id
#        5 -> gin_id
#        6 to 57 -> discard_id card_id
#        58 to 109 -> knock_id card_id
# ====================================

score_player_0_action_id = 0
score_player_1_action_id = 1
draw_card_action_id = 2
pick_up_discard_action_id = 3
declare_dead_hand_action_id = 4
gin_action_id = 5
discard_action_id = 6
knock_action_id = discard_action_id + 52


class ActionEvent(object):

    def __init__(self, action_id: int):
        self.action_id = action_id

    def __eq__(self, other):
        result = False
        if isinstance(other, ActionEvent):
            result = self.action_id == other.action_id
        return result

    @staticmethod
    def get_num_actions():
        ''' Return the number of possible actions in the game
        '''
        return knock_action_id + 52  # FIXME: sensitive to code changes 200213

    @staticmethod
    def decode_action(action_id) -> 'ActionEvent':
        ''' Action id -> the action_event in the game.

        Args:
            action_id (int): the id of the action

        Returns:
            action (ActionEvent): the action that will be passed to the game engine.
        '''
        if action_id == score_player_0_action_id:
            action_event = ScoreNorthPlayerAction()
        elif action_id == score_player_1_action_id:
            action_event = ScoreSouthPlayerAction()
        elif action_id == draw_card_action_id:
            action_event = DrawCardAction()
        elif action_id == pick_up_discard_action_id:
            action_event = PickUpDiscardAction()
        elif action_id == declare_dead_hand_action_id:
            action_event = DeclareDeadHandAction()
        elif action_id == gin_action_id:
            action_event = GinAction()
        elif action_id in range(discard_action_id, discard_action_id + 52):
            card_id = action_id - discard_action_id
            card = utils.get_card(card_id=card_id)
            action_event = DiscardAction(card=card)
        elif action_id in range(knock_action_id, knock_action_id + 52):
            card_id = action_id - knock_action_id
            card = utils.get_card(card_id=card_id)
            action_event = KnockAction(card=card)
        else:
            raise Exception("decode_action: unknown action_id={}".format(action_id))
        return action_event


class ScoreNorthPlayerAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=score_player_0_action_id)

    def __str__(self):
        return "score N"


class ScoreSouthPlayerAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=score_player_1_action_id)

    def __str__(self):
        return "score S"


class DrawCardAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=draw_card_action_id)

    def __str__(self):
        return "draw_card"


class PickUpDiscardAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=pick_up_discard_action_id)

    def __str__(self):
        return "pick_up_discard"


class DeclareDeadHandAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=declare_dead_hand_action_id)

    def __str__(self):
        return "declare_dead_hand"


class GinAction(ActionEvent):

    def __init__(self):
        super().__init__(action_id=gin_action_id)

    def __str__(self):
        return "gin"


class DiscardAction(ActionEvent):

    def __init__(self, card: Card):
        card_id = utils.get_card_id(card)
        super().__init__(action_id=discard_action_id + card_id)
        self.card = card

    def __str__(self):
        return "discard {}".format(str(self.card))


class KnockAction(ActionEvent):

    def __init__(self, card: Card):
        card_id = utils.get_card_id(card)
        super().__init__(action_id=knock_action_id + card_id)
        self.card = card

    def __str__(self):
        return "knock {}".format(str(self.card))
