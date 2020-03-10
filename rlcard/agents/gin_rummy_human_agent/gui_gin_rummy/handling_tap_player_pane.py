#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem
from .player_type import PlayerType


def handle_tap_player_pane(hit_item: CanvasItem, event, game_canvas: 'GameCanvas'):
    current_player_id = game_canvas.current_player_id
    current_player_is_human = game_canvas.player_types[current_player_id] is PlayerType.human_player
    # FIXME: stub for arranging held_pile
