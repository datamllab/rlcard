'''
    File name: gin_rummy/judge.py
    Author: William Hale
    Date created: 2/12/2020
'''

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.card import Card
from rlcard.games.gin_rummy.game import GinRummyGame

from typing import List

import rlcard.games.gin_rummy.utils.melding as melding
import rlcard.games.gin_rummy.utils.utils as utils


class GinRummyJudge(object):

    '''
        Judge decides legal actions for current player
    '''

    def __init__(self, game: GinRummyGame):
        ''' Initialize the class GinRummyJudge
        :param game: GinRummyGame
        '''
        self.game = game

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions = []
        last_action = self.game.get_last_action()
        last_action_type = type(last_action)
        if last_action is None or \
                last_action_type is DrawCardAction or \
                last_action_type is PickUpDiscardAction:
            current_player = self.game.get_current_player()
            hand = current_player.hand
            if self.game.settings.is_allowed_gin and can_gin(self.game):
                legal_actions = [GinAction()]
            else:
                cards_to_discard = [card for card in hand]
                if last_action_type is PickUpDiscardAction:
                    if not self.game.settings.is_allowed_to_discard_picked_up_card:
                        picked_up_card = self.game.round.move_sheet[-1].card
                        cards_to_discard.remove(picked_up_card)
                discard_actions = [DiscardAction(card=card) for card in cards_to_discard]
                legal_actions = discard_actions
                if self.game.settings.is_allowed_knock:
                    if current_player.player_id == 0 or not self.game.settings.is_south_never_knocks:
                        knock_cards = get_knock_cards(self.game)
                        if knock_cards:
                            knock_actions = [KnockAction(card=card) for card in knock_cards]
                            if not self.game.settings.is_always_knock:
                                legal_actions.extend(knock_actions)
                            else:
                                legal_actions = knock_actions
        elif last_action_type is DeclareDeadHandAction:
            legal_actions = [ScoreNorthPlayerAction()]
        elif last_action_type is GinAction:
            legal_actions = [ScoreNorthPlayerAction()]
        elif last_action_type is DiscardAction:
            can_draw_card = len(self.game.round.dealer.stock_pile) > self.game.settings.stockpile_dead_card_count
            if self.game.settings.max_drawn_card_count < 52:  # NOTE: this
                drawn_card_actions = [action for action in self.game.actions if type(action) is DrawCardAction]
                if len(drawn_card_actions) >= self.game.settings.max_drawn_card_count:
                    can_draw_card = False
            if can_draw_card:
                legal_actions = [DrawCardAction()]
                if self.game.settings.is_allowed_pick_up_discard:
                    legal_actions.append(PickUpDiscardAction())
            else:
                legal_actions = [DeclareDeadHandAction()]
                if self.game.settings.is_allowed_pick_up_discard:
                    legal_actions.append(PickUpDiscardAction())
        elif last_action_type is KnockAction:
            legal_actions = [ScoreNorthPlayerAction()]
        elif last_action_type is ScoreNorthPlayerAction:
            legal_actions = [ScoreSouthPlayerAction()]
        elif last_action_type is ScoreSouthPlayerAction:
            pass
        else:
            raise Exception('get_legal_actions: unknown last_action={}'.format(last_action))
        return legal_actions


def can_gin(game: GinRummyGame) -> bool:
    result = False
    last_action = game.get_last_action()
    last_action_type = type(last_action)
    if last_action_type is DrawCardAction or last_action_type is PickUpDiscardAction:
        current_player = game.get_current_player()
        hand = current_player.hand
        going_out_deadwood_count = game.settings.going_out_deadwood_count
        meld_clusters = melding.get_meld_clusters(hand=hand,
                                                  going_out_deadwood_count=going_out_deadwood_count,
                                                  is_going_out=True)
        if meld_clusters:
            deadwood_counts = [utils.get_deadwood_count(hand, meld_cluster) for meld_cluster in meld_clusters]
            result = min(deadwood_counts) == 0
    return result


def get_knock_cards(game: GinRummyGame) -> List[Card]:
    """
    :param game: GinRummyGame
    :return: list[Card] of cards that player can knock with
    """
    knock_cards = set()
    last_action = game.get_last_action()
    last_action_type = type(last_action)
    if last_action_type is DrawCardAction or last_action_type is PickUpDiscardAction:
        current_player = game.get_current_player()
        hand = current_player.hand
        going_out_deadwood_count = game.settings.going_out_deadwood_count
        meld_clusters = melding.get_meld_clusters(hand=hand,
                                                  going_out_deadwood_count=going_out_deadwood_count,
                                                  is_going_out=True)
        deadwood_cluster = [utils.get_deadwood(hand, meld_cluster) for meld_cluster in meld_clusters]
        for deadwood in deadwood_cluster:
            for card in deadwood:
                knock_cards.add(card)
    return list(knock_cards)
