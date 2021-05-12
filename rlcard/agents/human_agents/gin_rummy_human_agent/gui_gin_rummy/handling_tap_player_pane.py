'''
    Project: Gui Gin Rummy
    File name: handling_tap_player_pane.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from . import configurations
from . import utils

from .canvas_item import CanvasItem


def handle_tap_player_pane(hit_item: CanvasItem, event, game_canvas: 'GameCanvas'):
    # un-select and un-jog all held cards
    player_id = None
    if game_canvas.player_panes[0] == hit_item:
        player_id = 0
    elif game_canvas.player_panes[1] == hit_item:
        player_id = 1
    if player_id is not None and game_canvas.query.is_human(player_id):
        held_pile_item_ids = game_canvas.getter.get_held_pile_item_ids(player_id)
        for item_id in held_pile_item_ids:
            game_canvas.dtag(item_id, configurations.JOGGED_TAG)
            game_canvas.dtag(item_id, configurations.SELECTED_TAG)
        utils.fan_held_pile(player_id=player_id, game_canvas=game_canvas)
