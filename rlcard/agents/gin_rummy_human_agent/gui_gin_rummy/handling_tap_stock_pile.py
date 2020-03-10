#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.exceptions as exceptions
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.query as query
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.utils as utils


def handle_tap_stock_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):  # hit_item is source
    # Normal case is can_draw_from_stock_pile.
    # hit_item must not be drawn.
    # hit_item must be top card of stock_pile.
    # reset top card of discard pile if drawn.
    # reset all selected cards in held_pile
    if game_canvas.is_game_over():
        pass
    elif query.can_discard_card(game_canvas):
        pass
    elif query.can_declare_dead_hand(game_canvas):
        pass
    elif query.can_draw_from_stock_pile(game_canvas):
        current_player_id = game_canvas.current_player_id
        hit_item_tags = hit_item.get_tags()
        if configurations.DRAWN_TAG not in hit_item_tags:
            top_stock_pile_item_id = game_canvas.get_top_stock_pile_item_id()
            if hit_item == top_stock_pile_item_id:
                utils.toggle_stock_pile_item_selected(game_canvas)
                # reset drawn top card of discard_pile if needed
                top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
                top_discard_pile_item_tags = game_canvas.get_tags(top_discard_pile_item_id)
                if configurations.DRAWN_TAG in top_discard_pile_item_tags:
                    utils.toggle_discard_pile_item_selected(game_canvas=game_canvas)
                # reset selected cards of held_pile of current_player
                held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=current_player_id)
                for held_pile_item_id in held_pile_item_ids:
                    held_pile_item_tags = game_canvas.get_tags(item=held_pile_item_id)
                    if configurations.SELECTED_TAG in held_pile_item_tags:
                        utils.toggle_held_pile_item_selected(item=held_pile_item_id, game_canvas=game_canvas)
        else:
            raise exceptions.ProgramError  # FIXME: provide more information about error ???
