#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .player_type import PlayerType
from .canvas_item import CanvasItem

from .handling_tap_stock_pile import handle_tap_stock_pile
from .handling_tap_discard_pile import handle_tap_discard_pile
from .handling_tap_held_pile import handle_tap_held_pile
from .handling_tap_player_pane import handle_tap_player_pane

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations


def handle_tap(hit_item: CanvasItem, event, game_canvas: 'GameCanvas'):
    if hit_item in game_canvas.player_panes:
        handle_tap_player_pane(hit_item=hit_item, event=event, game_canvas=game_canvas)
    else:
        current_player_id = game_canvas.current_player_id
        if current_player_id is not None and game_canvas.player_types[current_player_id] is PlayerType.human_player:
            hit_item_tags = hit_item.get_tags()
            if configurations.STOCK_PILE_TAG in hit_item_tags:
                handle_tap_stock_pile(hit_item=hit_item, game_canvas=game_canvas)
            elif configurations.DISCARD_PILE_TAG in hit_item_tags or hit_item == game_canvas.discard_pile_box_item:
                handle_tap_discard_pile(hit_item=hit_item, game_canvas=game_canvas)
            elif game_canvas.held_pile_tags[current_player_id] in hit_item_tags:
                handle_tap_held_pile(hit_item=hit_item, game_canvas=game_canvas)
