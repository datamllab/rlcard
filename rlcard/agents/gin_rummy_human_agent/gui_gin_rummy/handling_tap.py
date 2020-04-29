'''
    Project: Gui Gin Rummy
    File name: handling_tap.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from . import configurations
from . import starting_new_game

from .canvas_item import CanvasItem
from .handling_tap_stock_pile import handle_tap_stock_pile
from .handling_tap_discard_pile import handle_tap_discard_pile
from .handling_tap_held_pile import handle_tap_held_pile
from .handling_tap_player_pane import handle_tap_player_pane

from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError


def on_game_canvas_tap(event):
    widget = event.widget
    hit_item_ids = widget.find_withtag("current")
    if hit_item_ids:
        if not len(hit_item_ids) == 1:
            raise GinRummyProgramError("len(hit_item_ids)={} must be 1.".format(len(hit_item_ids)))
        hit_item_id = hit_item_ids[0]
        hit_item = None
        for canvas_item in widget.canvas_items:
            if canvas_item.item_id == hit_item_id:
                hit_item = canvas_item
        if hit_item:
            if not widget.query.is_game_over():
                _handle_tap(hit_item=hit_item, event=event, game_canvas=widget)
            else:
                top_discard_pile_item_id = widget.getter.get_top_discard_pile_item_id()
                if hit_item_id == top_discard_pile_item_id:
                    starting_new_game.start_new_game(game_canvas=widget)


def _handle_tap(hit_item: CanvasItem, event, game_canvas: 'GameCanvas'):
    hit_item_tags = hit_item.get_tags()
    if configurations.STOCK_PILE_TAG in hit_item_tags:
        current_player_id = game_canvas.current_player_id
        current_player_is_human = game_canvas.query.is_human(player_id=current_player_id)
        if current_player_is_human:
            handle_tap_stock_pile(hit_item=hit_item, game_canvas=game_canvas)
    elif configurations.DISCARD_PILE_TAG in hit_item_tags or hit_item == game_canvas.discard_pile_box_item:
        current_player_id = game_canvas.current_player_id
        current_player_is_human = game_canvas.query.is_human(player_id=current_player_id)
        if current_player_is_human:
            handle_tap_discard_pile(hit_item=hit_item, game_canvas=game_canvas)
    elif game_canvas.held_pile_tags[0] in hit_item_tags:
        pass  # north player is never human player
    elif game_canvas.held_pile_tags[1] in hit_item_tags:
        handle_tap_held_pile(hit_item=hit_item, game_canvas=game_canvas)
    elif hit_item == game_canvas.player_panes[0]:
        pass  # north player is never human player
    elif hit_item == game_canvas.player_panes[1]:
        handle_tap_player_pane(hit_item=hit_item, event=event, game_canvas=game_canvas)
