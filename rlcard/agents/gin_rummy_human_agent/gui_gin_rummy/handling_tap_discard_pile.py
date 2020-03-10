#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem

import examples.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import examples.gin_rummy_human_agent.gui_gin_rummy.exceptions as exceptions
import examples.gin_rummy_human_agent.gui_gin_rummy.post_doing_action as post_doing_action
import examples.gin_rummy_human_agent.gui_gin_rummy.query as query
import examples.gin_rummy_human_agent.gui_gin_rummy.starting_new_game as starting_new_game
import examples.gin_rummy_human_agent.gui_gin_rummy.utils as utils


def handle_tap_discard_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    if game_canvas.is_game_over():
        starting_new_game.start_new_game(game_canvas)
    else:
        if query.can_draw_from_discard_pile(game_canvas):
            handle_can_draw_from_discard_pile(hit_item=hit_item, game_canvas=game_canvas)
        elif query.can_discard_card(game_canvas):
            handle_can_discard_card(hit_item=hit_item, game_canvas=game_canvas)
        else:
            raise exceptions.GinRummyError  # FIXME: better error name


def handle_can_draw_from_discard_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):  # hit_item is source
    # hit_item must be top card of discard_pile.
    # Normal case is to toggle jog the top card of the discard pile.
    # Special case is to discard the card drawn from stockpile before being placed in held_pile.
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    if hit_item.item_id == top_discard_pile_item_id:
        env_controller = game_canvas.env_controller
        top_stock_pile_item_id = game_canvas.get_top_stock_pile_item_id()
        top_stock_pile_item_tags = game_canvas.get_tags(top_stock_pile_item_id)
        if configurations.DRAWN_TAG in top_stock_pile_item_tags:
            post_doing_action.post_do_discard_card_drawn_from_stock_pile_action(top_stock_pile_item_id,
                                                                                env_controller=env_controller)
        else:
            utils.toggle_discard_pile_item_selected(game_canvas=game_canvas)
    else:
        pass  # FIXME: put warning message ???


def handle_can_discard_card(hit_item: CanvasItem, game_canvas: 'GameCanvas'):  # hit_item is target
    # hit_item must be top card of discard_pile or discard_pile_box_item.
    # exactly one held_pile_item must be selected.
    # The selected held_pile_item is discarded.
    # The remaining held_pile_items are fanned.
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    if top_discard_pile_item_id:
        assert hit_item == top_discard_pile_item_id
    else:
        assert hit_item == game_canvas.discard_pile_box_item
    current_player_id = game_canvas.current_player_id
    selected_held_pile_item_ids = game_canvas.get_selected_held_pile_item_ids(player_id=current_player_id)
    if len(selected_held_pile_item_ids) == 1:
        selected_held_pile_item_id = selected_held_pile_item_ids[0]
        post_doing_action.post_do_discard_action(selected_held_pile_item_id, env_controller=game_canvas.env_controller)
    else:
        pass  # FIXME: put warning message ???
