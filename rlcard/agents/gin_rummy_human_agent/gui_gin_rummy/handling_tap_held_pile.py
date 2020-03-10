#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .player_type import PlayerType
from .canvas_item import CanvasItem

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.post_doing_action as post_doing_action
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.exceptions as exceptions
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.query as query
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.utils as utils


def handle_tap_held_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    # hit_item must be held_pile_item of current_player_id.
    current_player_id = game_canvas.current_player_id
    current_player_is_human = game_canvas.player_types[current_player_id] is PlayerType.human_player
    can_draw_from_stock_pile = query.can_draw_from_stock_pile(game_canvas)
    can_draw_from_discard_pile = query.can_draw_from_discard_pile(game_canvas)
    is_game_over = game_canvas.is_game_over()
    if is_game_over:
        pass
    elif query.can_discard_card(game_canvas):  # hit_item is source
        if current_player_is_human:
            utils.toggle_held_pile_item_selected(item=hit_item, game_canvas=game_canvas)
    elif can_draw_from_stock_pile or can_draw_from_discard_pile:  # hit_item is target
        drawn_card_item_id = None
        drawn_card_item_tag = None
        if not drawn_card_item_id and can_draw_from_stock_pile:
            top_stock_pile_item_id = game_canvas.get_top_stock_pile_item_id()
            top_stock_pile_item_tags = game_canvas.get_tags(top_stock_pile_item_id)
            if configurations.DRAWN_TAG in top_stock_pile_item_tags:
                drawn_card_item_id = top_stock_pile_item_id
                drawn_card_item_tag = configurations.STOCK_PILE_TAG
        if not drawn_card_item_id and can_draw_from_discard_pile:
            top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
            top_discard_pile_item_tags = game_canvas.get_tags(top_discard_pile_item_id)
            if configurations.DRAWN_TAG in top_discard_pile_item_tags:
                drawn_card_item_id = top_discard_pile_item_id
                drawn_card_item_tag = configurations.DISCARD_PILE_TAG
        if drawn_card_item_id:
            post_doing_action.post_do_get_card_action(drawn_card_item_id=drawn_card_item_id,
                                                      hit_item_id=hit_item.item_id,
                                                      drawn_card_item_tag=drawn_card_item_tag,
                                                      env_controller=game_canvas.env_controller)
        else:
            utils.toggle_held_pile_item_selected(item=hit_item, game_canvas=game_canvas)
    else:
        raise exceptions.GinRummyError  # FIXME: better error name
