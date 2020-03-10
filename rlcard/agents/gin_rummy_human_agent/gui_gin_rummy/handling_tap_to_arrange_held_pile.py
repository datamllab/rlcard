#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem
from .player_type import PlayerType

import examples.gin_rummy_human_agent.gui_gin_rummy.query as query
import examples.gin_rummy_human_agent.gui_gin_rummy.utils as utils


def handle_tap_to_arrange_held_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    # game is not over.
    # tapper_id must be human_player.
    if not game_canvas.is_game_over():
        hit_item_tags = hit_item.get_tags()
        arranger_id = None
        for player_id in range(2):
            held_pile_tag = game_canvas.held_pile_tags[player_id]
            if held_pile_tag in hit_item_tags:
                arranger_id = player_id
        if arranger_id is not None and game_canvas.player_types[arranger_id] is PlayerType.human_player:
            held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=arranger_id)
            selected_item_ids = [item for item in held_pile_item_ids if query.is_item_selected(game_canvas, item=item)]
            if selected_item_ids:
                utils.drop_item_ids(item_ids=selected_item_ids, on_item_id=hit_item.item_id,
                                    player_id=arranger_id, game_canvas=game_canvas)
