'''
    Project: Gui Gin Rummy
    File name: handling_tap_discard_pile.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem

from . import configurations
from . import info_messaging
from . import starting_new_game
from . import utils

from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError


def handle_tap_discard_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    player_id = game_canvas.current_player_id
    if game_canvas.query.is_game_over():
        starting_new_game.start_new_game(game_canvas)
    else:
        if game_canvas.query.can_draw_from_discard_pile(player_id=player_id):
            _handle_can_draw_from_discard_pile(hit_item=hit_item, game_canvas=game_canvas)
        elif game_canvas.query.can_discard_card(player_id=player_id):
            _handle_can_discard_card(hit_item=hit_item, game_canvas=game_canvas)
        else:
            pass  # FIXME: put warning message ???


#
#   Private methods
#

def _handle_can_draw_from_discard_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):  # hit_item is source
    # hit_item must be top card of discard_pile.
    # Normal case is to toggle jog the top card of the discard pile.
    # Special case is to discard the card drawn from stockpile before being placed in held_pile.
    top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
    if hit_item.item_id == top_discard_pile_item_id:
        top_stock_pile_item_id = game_canvas.getter.get_top_stock_pile_item_id()
        top_stock_pile_item_tags = game_canvas.getter.get_tags(top_stock_pile_item_id)
        if configurations.DRAWN_TAG in top_stock_pile_item_tags:
            game_canvas.post_doing_action.post_do_discard_card_drawn_from_stock_pile_action(top_stock_pile_item_id)
        else:
            utils.toggle_discard_pile_item_selected(game_canvas=game_canvas)
    else:
        pass  # FIXME: put warning message ???


def _handle_can_discard_card(hit_item: CanvasItem, game_canvas: 'GameCanvas'):  # hit_item is target
    # hit_item must be top card of discard_pile or discard_pile_box_item.
    # exactly one held_pile_item must be selected.
    # The selected held_pile_item is discarded.
    # The remaining held_pile_items are fanned.
    top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
    if top_discard_pile_item_id:
        if not hit_item == top_discard_pile_item_id:
            raise GinRummyProgramError("hit_item must be top card of discard_pile.")
    else:
        if not hit_item == game_canvas.discard_pile_box_item:
            raise GinRummyProgramError("hit_item must be discard_pile_box_item.")
    current_player_id = game_canvas.current_player_id
    selected_held_pile_item_ids = game_canvas.getter.get_selected_held_pile_item_ids(player_id=current_player_id)
    if len(selected_held_pile_item_ids) == 1:
        if current_player_id == 1:  # remove info_message if south player
            info_messaging.blank_info_message_label(game_canvas=game_canvas)
        selected_held_pile_item_id = selected_held_pile_item_ids[0]
        game_canvas.post_doing_action.post_do_discard_action(player_id=current_player_id,
                                                             selected_held_pile_item_id=selected_held_pile_item_id)
    else:
        pass  # FIXME: put warning message ???
