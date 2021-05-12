'''
    Project: Gui Gin Rummy
    File name: game_canvas_getter.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from typing import List

from rlcard.games.gin_rummy.utils.action_event import *
from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError

import rlcard.games.gin_rummy.judge as judge
import rlcard.games.gin_rummy.utils.utils as gin_rummy_utils

from rlcard.games.gin_rummy.game import GinRummyGame

# GinRummyMoves
from rlcard.games.gin_rummy.utils.move import GinRummyMove
from rlcard.games.gin_rummy.utils.move import DealHandMove
from rlcard.games.gin_rummy.utils.move import DrawCardMove, PickupDiscardMove, DeclareDeadHandMove
from rlcard.games.gin_rummy.utils.move import DiscardMove, KnockMove, GinMove
from rlcard.games.gin_rummy.utils.move import ScoreNorthMove, ScoreSouthMove
from rlcard.games.gin_rummy.utils.settings import Settings

from . import configurations


class GameCanvasGetter(object):

    def __init__(self, game_canvas: 'GameCanvas'):
        self.game_canvas = game_canvas

    def get_game(self) -> GinRummyGame:
        return self.game_canvas.game_canvas_updater.env_thread.gin_rummy_env.game

    def get_settings(self) -> Settings:
        return self.game_canvas.game_canvas_updater.env_thread.gin_rummy_env.game.settings

    def get_game_canvas_moves(self) -> List[GinRummyMove]:
        result = []  # type: List[GinRummyMove]
        game = self.get_game()
        if game.round:
            game_canvas = self.game_canvas
            mark = game_canvas.game_canvas_updater.mark
            result = game.round.move_sheet[:mark]
        return result

    def get_current_player_id(self) -> int or None:
        result = None  # type: int or None
        game = self.get_game()
        if not game.round:
            return None
        game_canvas = self.game_canvas
        mark = game_canvas.game_canvas_updater.mark
        moves = game.round.move_sheet[:mark]
        if not moves:
            if not mark == 0:
                raise GinRummyProgramError("mark={} must be 0.".format(mark))
            if game.round.move_sheet:
                first_move = game.round.move_sheet[0]
                if isinstance(first_move, DealHandMove):
                    result = first_move.player_dealing.player_id
        else:
            last_move = moves[-1]
            if isinstance(last_move, DealHandMove):
                result = (last_move.player_dealing.player_id + 1) % 2
            elif isinstance(last_move, DrawCardMove):
                result = last_move.player.player_id
            elif isinstance(last_move, PickupDiscardMove):
                result = last_move.player.player_id
            elif isinstance(last_move, DeclareDeadHandMove):
                result = 0
            elif isinstance(last_move, DiscardMove):
                penultimate_move = moves[-2]
                can_keep_turn = configurations.IS_KEEP_TURN_WHEN_DISCARDING_CARD_PICKED_UP
                is_discarding_card_picked_up = False
                if isinstance(penultimate_move, PickupDiscardMove) and last_move.action.card == penultimate_move.card:
                    is_discarding_card_picked_up = True
                if is_discarding_card_picked_up and can_keep_turn:
                    result = last_move.player.player_id  # keep turn when discarding card picked up
                else:
                    result = (last_move.player.player_id + 1) % 2
            elif isinstance(last_move, KnockMove):
                result = 0
            elif isinstance(last_move, GinMove):
                result = 0
            elif isinstance(last_move, ScoreNorthMove):
                result = 1
            elif isinstance(last_move, ScoreSouthMove):
                pass
            else:
                raise GinRummyProgramError('get_current_player_id: unknown last_move={}'.format(last_move))
        return result

    def get_legal_actions(self, player_id: int) -> List[ActionEvent]:
        if player_id != self.get_current_player_id():
            return []
        legal_actions = []  # type: List[ActionEvent]
        game = self.get_game()
        game_canvas = self.game_canvas
        moves = game.round.move_sheet[:game_canvas.game_canvas_updater.mark]
        last_move = None if not moves else moves[-1]
        if not last_move:
            return []
        settings = self.get_settings()
        if isinstance(last_move, DealHandMove) or \
                isinstance(last_move, DrawCardMove) or \
                isinstance(last_move, PickupDiscardMove):
            going_out_deadwood_count = settings.going_out_deadwood_count
            hand = self.get_held_pile_cards(player_id=player_id)
            knock_cards, gin_cards = judge.get_going_out_cards(hand=hand, going_out_deadwood_count=going_out_deadwood_count)
            if settings.is_allowed_gin and gin_cards:
                legal_actions = [GinAction()]
            else:
                cards_to_discard = [card for card in hand]
                if isinstance(last_move, PickupDiscardMove):
                    if not settings.is_allowed_to_discard_picked_up_card:
                        picked_up_card = last_move.card
                        cards_to_discard.remove(picked_up_card)
                discard_actions = [DiscardAction(card=card) for card in cards_to_discard]
                legal_actions = discard_actions
                if settings.is_allowed_knock:
                    if player_id == 0 or not settings.is_south_never_knocks:
                        if knock_cards:
                            knock_actions = [KnockAction(card=card) for card in knock_cards]
                            if not settings.is_always_knock:
                                legal_actions.extend(knock_actions)
                            else:
                                legal_actions = knock_actions
        elif isinstance(last_move, DeclareDeadHandMove):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_move, GinMove):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_move, DiscardMove):
            stock_pile_item_ids = self.get_stock_pile_item_ids()
            can_draw_card = len(stock_pile_item_ids) > settings.stockpile_dead_card_count
            if settings.max_drawn_card_count < 52:  # NOTE: this
                draw_card_moves = [x for x in moves if isinstance(x, DrawCardMove)]
                if len(draw_card_moves) >= settings.max_drawn_card_count:
                    can_draw_card = False
            if can_draw_card:
                legal_actions = [DrawCardAction()]
                if settings.is_allowed_pick_up_discard:
                    legal_actions.append(PickUpDiscardAction())
            else:
                legal_actions = [DeclareDeadHandAction()]
                if settings.is_allowed_pick_up_discard:
                    legal_actions.append(PickUpDiscardAction())
        elif isinstance(last_move, KnockMove):
            legal_actions = [ScoreNorthPlayerAction()]
        elif isinstance(last_move, ScoreNorthMove):
            legal_actions = [ScoreSouthPlayerAction()]
        elif isinstance(last_move, ScoreSouthMove):
            pass
        else:
            raise GinRummyProgramError('get_legal_actions: unknown last_move={}'.format(last_move))
        return legal_actions

    def get_tags(self, item_id) -> List[str]:
        return [] if not item_id else self.game_canvas.itemcget(item_id, 'tags')

    def get_card_id(self, card_item_id: int) -> int:
        game_canvas = self.game_canvas
        if card_item_id in game_canvas.card_item_ids:
            card_id = game_canvas.card_item_ids.index(card_item_id)
        else:
            raise GinRummyProgramError("card_item_id={} not found in card_item_ids.".format(card_item_id))
        return card_id

    def get_top_discard_pile_item_id(self) -> int or None:
        game_canvas = self.game_canvas
        discard_pile_item_ids = game_canvas.find_withtag(configurations.DISCARD_PILE_TAG)
        return None if not discard_pile_item_ids else discard_pile_item_ids[-1]

    def get_top_stock_pile_item_id(self) -> int or None:
        game_canvas = self.game_canvas
        stock_pile_item_ids = game_canvas.find_withtag(configurations.STOCK_PILE_TAG)
        return None if not stock_pile_item_ids else stock_pile_item_ids[-1]

    def get_stock_pile_item_ids(self) -> List[int]:
        game_canvas = self.game_canvas
        stock_pile_item_ids = game_canvas.find_withtag(configurations.STOCK_PILE_TAG)
        return stock_pile_item_ids

    def get_held_pile_item_ids(self, player_id: int) -> List[int]:
        if player_id is None:
            raise GinRummyProgramError("player_id must not be None.")
        game_canvas = self.game_canvas
        ghost_card_item = game_canvas.held_pile_ghost_card_items[player_id]
        held_pile_tag = game_canvas.held_pile_tags[player_id]
        held_pile_item_ids = [x for x in game_canvas.find_withtag(held_pile_tag) if x != ghost_card_item]
        return held_pile_item_ids

    def get_held_pile_cards(self, player_id: int) -> List[Card]:
        held_pile_item_ids = self.get_held_pile_item_ids(player_id=player_id)
        held_pile_card_ids = [self.get_card_id(card_item_id=x) for x in held_pile_item_ids]
        held_pile_cards = [gin_rummy_utils.card_from_card_id(card_id) for card_id in held_pile_card_ids]
        return held_pile_cards

    def get_selected_held_pile_item_ids(self, player_id: int) -> List[int]:
        game_canvas = self.game_canvas
        held_pile_item_ids = self.get_held_pile_item_ids(player_id)
        selected_item_ids = game_canvas.find_withtag(configurations.SELECTED_TAG)
        selected_held_pile_item_ids = [x for x in selected_item_ids if x in held_pile_item_ids]
        return selected_held_pile_item_ids
