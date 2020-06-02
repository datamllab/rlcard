'''
    Project: Gui Gin Rummy
    File name: handling_tap_to_arrange_held_pile.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from .canvas_item import CanvasItem
from .player_type import PlayerType

from . import handling_tap
from . import utils

from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError


def on_tap_to_arrange_held_pile(event):
    widget = event.widget
    if widget.query.is_game_over():
        return
    # game must not be over
    hit_items_ids = widget.find_withtag("current")
    if not hit_items_ids:
        return
    if not len(hit_items_ids) == 1:
        raise GinRummyProgramError("len(hit_items_ids)={} must be 1.".format(len(hit_items_ids)))
    hit_item_id = hit_items_ids[0]
    hit_item = None
    for canvas_item in widget.canvas_items:
        if canvas_item.item_id == hit_item_id:
            hit_item = canvas_item
    if hit_item:
        hit_item_tags = hit_item.get_tags()
        hit_held_pile_tag = None
        for held_pile_tag in widget.held_pile_tags:
            if held_pile_tag in hit_item_tags:
                hit_held_pile_tag = held_pile_tag
                break
        if not hit_held_pile_tag:
            return
        # must hit a held_pile
        hitter_id = widget.held_pile_tags.index(hit_held_pile_tag)
        if widget.player_types[hitter_id] is not PlayerType.human_player:
            return
        # held_pile hit must belong to human player
        must_do_on_tap = False
        if hitter_id == widget.current_player_id:
            is_top_discard_pile_item_drawn = widget.query.is_top_discard_pile_item_drawn()
            is_top_stock_pile_item_drawn = widget.query.is_top_stock_pile_item_drawn()
            must_do_on_tap = is_top_discard_pile_item_drawn or is_top_stock_pile_item_drawn
        if must_do_on_tap:
            # Minor kludge to handle the following situation.
            # The current_player should just tap to combine drawn card with the selected cards.
            # However, I suspect the player will get in the habit of treating this situation as an arrangement.
            handling_tap.on_game_canvas_tap(event)  # kludge
        else:
            handle_tap_to_arrange_held_pile(hit_item=hit_item, game_canvas=widget)


def handle_tap_to_arrange_held_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    # game is not over.
    # tapper_id must be human_player.
    if not game_canvas.query.is_game_over():
        hit_item_tags = hit_item.get_tags()
        arranger_id = None
        for player_id in range(2):
            held_pile_tag = game_canvas.held_pile_tags[player_id]
            if held_pile_tag in hit_item_tags:
                arranger_id = player_id
        if arranger_id is not None and game_canvas.player_types[arranger_id] is PlayerType.human_player:
            held_pile_item_ids = game_canvas.getter.get_held_pile_item_ids(player_id=arranger_id)
            selected_item_ids = [x for x in held_pile_item_ids if game_canvas.query.is_item_id_selected(item_id=x)]
            if selected_item_ids:
                utils.drop_item_ids(item_ids=selected_item_ids, on_item_id=hit_item.item_id,
                                    player_id=arranger_id, game_canvas=game_canvas)
