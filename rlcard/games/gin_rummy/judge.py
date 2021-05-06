'''
    File name: gin_rummy/judge.py
    Author: William Hale
    Date created: 2/12/2020
'''

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game import GinRummyGame

from typing import List, Tuple

from .utils.action_event import *
from .utils.scorers import GinRummyScorer
from .utils import melding
from .utils.gin_rummy_error import GinRummyProgramError

from rlcard.games.gin_rummy.utils import utils


class GinRummyJudge:

    '''
        Judge decides legal actions for current player
    '''

    def __init__(self, game: 'GinRummyGame'):
        ''' Initialize the class GinRummyJudge
        :param game: GinRummyGame
        '''
        self.game = game
        self.scorer = GinRummyScorer()

    def get_legal_actions(self) -> List[ActionEvent]:
        """
        :return: List[ActionEvent] of legal actions
        """
        legal_actions = []  # type: List[ActionEvent]
        last_action = self.game.get_last_action()
        if last_action is None or \
                isinstance(last_action, DrawCardAction) or \
                isinstance(last_action, PickUpDiscardAction):
            current_player = self.game.get_current_player()
            going_out_deadwood_count = self.game.settings.going_out_deadwood_count
            hand = current_player.hand
            meld_clusters = current_player.get_meld_clusters()  # improve speed 2020-Apr
            knock_cards, gin_cards = _get_going_out_cards(meld_clusters=meld_clusters,
                                                          hand=hand,
                                                          going_out_deadwood_count=going_out_deadwood_count)
            if self.game.settings.is_allowed_gin and gin_cards:
                legal_actions = [GinAction()]
            else:
                cards_to_discard = [card for card in hand]
                if isinstance(last_action, PickUpDiscardAction):
                    if not self.game.settings.is_allowed_to_discard_picked_up_card:
                        picked_up_card = self.game.round.move_sheet[-1].card
                        cards_to_discard.remove(picked_up_card)
                discard_actions = [DiscardAction(card=card) for card in cards_to_discard]
                legal_actions = discard_actions
                if self.game.settings.is_allowed_knock:
                    if current_player.player_id == 0 or not self.game.settings.is_south_never_knocks:
                        if knock_cards:
                            knock_actions = [KnockAction(card=card) for card in knock_cards]
                            if not self.game.settings.is_always_knock:
                                legal_actions.extend(knock_actions)
                            else:
                                legal_actions = knock_actions
        elif isinstance(last_action, DeclareDeadHandAction):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_action, GinAction):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_action, DiscardAction):
            can_draw_card = len(self.game.round.dealer.stock_pile) > self.game.settings.stockpile_dead_card_count
            if self.game.settings.max_drawn_card_count < 52:  # NOTE: this
                drawn_card_actions = [action for action in self.game.actions if isinstance(action, DrawCardAction)]
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
        elif isinstance(last_action, KnockAction):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_action, ScoreNorthPlayerAction):
            legal_actions = [ScoreSouthPlayerAction()]
        elif isinstance(last_action, ScoreSouthPlayerAction):
            pass
        else:
            raise Exception('get_legal_actions: unknown last_action={}'.format(last_action))
        return legal_actions


def get_going_out_cards(hand: List[Card], going_out_deadwood_count: int) -> Tuple[List[Card], List[Card]]:
    '''
    :param hand: List[Card] -- must have 11 cards
    :param going_out_deadwood_count: int
    :return List[Card], List[Card: cards in hand that be knocked, cards in hand that can be ginned
    '''
    if not len(hand) == 11:
        raise GinRummyProgramError("len(hand) is {}: should be 11.".format(len(hand)))
    meld_clusters = melding.get_meld_clusters(hand=hand)
    knock_cards, gin_cards = _get_going_out_cards(meld_clusters=meld_clusters,
                                                  hand=hand,
                                                  going_out_deadwood_count=going_out_deadwood_count)
    return list(knock_cards), list(gin_cards)


#
# private methods
#

def _get_going_out_cards(meld_clusters: List[List[List[Card]]],
                         hand: List[Card],
                         going_out_deadwood_count: int) -> Tuple[List[Card], List[Card]]:
    '''
    :param meld_clusters
    :param hand: List[Card] -- must have 11 cards
    :param going_out_deadwood_count: int
    :return List[Card], List[Card: cards in hand that be knocked, cards in hand that can be ginned
    '''
    if not len(hand) == 11:
        raise GinRummyProgramError("len(hand) is {}: should be 11.".format(len(hand)))
    knock_cards = set()
    gin_cards = set()
    for meld_cluster in meld_clusters:
        meld_cards = [card for meld_pile in meld_cluster for card in meld_pile]
        hand_deadwood = [card for card in hand if card not in meld_cards]  # hand has 11 cards
        if len(hand_deadwood) == 0:
            # all 11 cards are melded;
            # take gin_card as first card of first 4+ meld;
            # could also take gin_card as last card of 4+ meld, but won't do this.
            for meld_pile in meld_cluster:
                if len(meld_pile) >= 4:
                    gin_cards.add(meld_pile[0])
                    break
        elif len(hand_deadwood) == 1:
            card = hand_deadwood[0]
            gin_cards.add(card)
        else:
            hand_deadwood_values = [utils.get_deadwood_value(card) for card in hand_deadwood]
            hand_deadwood_count = sum(hand_deadwood_values)
            max_hand_deadwood_value = max(hand_deadwood_values, default=0)
            if hand_deadwood_count <= 10 + max_hand_deadwood_value:
                for card in hand_deadwood:
                    next_deadwood_count = hand_deadwood_count - utils.get_deadwood_value(card)
                    if next_deadwood_count <= going_out_deadwood_count:
                        knock_cards.add(card)
    return list(knock_cards), list(gin_cards)
