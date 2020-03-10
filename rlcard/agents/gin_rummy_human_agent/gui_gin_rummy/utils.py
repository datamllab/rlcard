#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from typing import List

import tkinter as tk

from .canvas_item import CardItem

from .configurations import SCORE_PLAYER_0_ACTION_ID, SCORE_PLAYER_1_ACTION_ID
from .configurations import DRAW_CARD_ACTION_ID, PICK_UP_DISCARD_ACTION_ID
from .configurations import DECLARE_DEAD_HAND_ACTION_ID
from .configurations import DISCARD_ACTION_ID, KNOCK_ACTION_ID

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.exceptions as exceptions


def gin_rummy_sort_order_id(card_id: int) -> int:
    return 4 * (card_id % 13) + (3 - card_id // 13)  # would have been better if card_id was specified in order wanted


def move_to(item_id: int, x: int, y: int, parent: tk.Canvas):
    parent.coords(item_id, x, y)


def translated_by(dx: float, dy: float, location):
    assert len(location) == 2
    return [location[0] + dx, location[1] + dy]


def player_short_name(player_id: int) -> str:
    return "N" if player_id == 0 else "S" if player_id == 1 else "X"


def get_action_type(action: int) -> int:
    if action == DRAW_CARD_ACTION_ID:
        result = action
    elif action == PICK_UP_DISCARD_ACTION_ID:
        result = action
    elif action == DECLARE_DEAD_HAND_ACTION_ID:
        result = action
    elif DISCARD_ACTION_ID <= action < DISCARD_ACTION_ID + 52:
        result = DISCARD_ACTION_ID
    elif KNOCK_ACTION_ID <= action < KNOCK_ACTION_ID + 52:
        result = KNOCK_ACTION_ID
    elif action == SCORE_PLAYER_0_ACTION_ID:
        result = action
    elif action == SCORE_PLAYER_1_ACTION_ID:
        result = action
    else:
        raise exceptions.GinRummyError(f"No action type for {action}.")
    return result


def get_action_card_id(action: int) -> int or None:
    result = None
    action_type = get_action_type(action)
    if action_type == DISCARD_ACTION_ID:
        result = action - DISCARD_ACTION_ID
    elif action_type == KNOCK_ACTION_ID:
        result = action - KNOCK_ACTION_ID
    return result


#   =========================================
#   Transformations (i.e. complex setter)
#   =========================================

def drop_item_ids(item_ids: List[int], on_item_id: int, player_id: int, game_canvas: 'GameCanvas'):
    # on_item_id must be in held_pile_item_ids of player_id
    # item_ids are inserted into held_pile of player_id after on_item_id
    held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id)
    held_pile_ghost_card_item = game_canvas.held_pile_ghost_card_items[player_id]
    assert on_item_id == held_pile_ghost_card_item or on_item_id in held_pile_item_ids
    held_pile_item_ids_count = len(held_pile_item_ids)
    held_pile_tag = game_canvas.held_pile_tags[player_id]
    on_item_index = -1 if on_item_id == held_pile_ghost_card_item else held_pile_item_ids.index(on_item_id)
    after_items = []
    for i in range(on_item_index + 1, held_pile_item_ids_count):
        after_item_id = held_pile_item_ids[i]
        if after_item_id not in item_ids:
            after_items.append(after_item_id)
    sorted_items = sorted(item_ids, reverse=True)  # FIXME: assuming that card_item_ids are in sorted order
    for item in sorted_items:
        item_tags = game_canvas.get_tags(item)
        if configurations.SELECTED_TAG in item_tags:
            game_canvas.dtag(item, configurations.SELECTED_TAG)
            game_canvas.dtag(item, configurations.JOGGED_TAG)
        if configurations.DRAWN_TAG in item_tags:
            game_canvas.dtag(item, configurations.DRAWN_TAG)
            if configurations.DISCARD_PILE_TAG in item_tags:
                game_canvas.dtag(item, configurations.DISCARD_PILE_TAG)
            elif configurations.STOCK_PILE_TAG in item_tags:
                game_canvas.dtag(item, configurations.STOCK_PILE_TAG)
            assert held_pile_tag not in item_tags
            game_canvas.addtag_withtag(held_pile_tag, item)
        game_canvas.tag_raise(item)
    for after_item in after_items:
        game_canvas.tag_raise(after_item)
    fan_held_pile(player_id, game_canvas=game_canvas)


def fan_held_pile(player_id: int, game_canvas: 'GameCanvas'):
    held_pile_tab = game_canvas.held_pile_tab
    held_pile_anchor = game_canvas.player_held_pile_anchors[player_id]
    held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=player_id)
    # right justify hand when melding
    dx = 0
    count = len(held_pile_item_ids)
    if count < 10:
        dx = (10 - count) * game_canvas.held_pile_tab
    x = held_pile_anchor[0] + dx
    y = held_pile_anchor[1]
    for held_pile_item_id in held_pile_item_ids:
        move_to(held_pile_item_id, x, y, parent=game_canvas)
        game_canvas.tag_raise(held_pile_item_id)
        x += held_pile_tab


def held_pile_insert(card_item_id: int, above_card_item_id: int or None, player_id: int, game_canvas: 'GameCanvas'):
    held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=player_id)
    held_pile_item_ids_count = len(held_pile_item_ids)
    if above_card_item_id is None or above_card_item_id == game_canvas.held_pile_ghost_card_items[player_id]:
        insertion_index = 0
    else:
        insertion_index = held_pile_item_ids.index(above_card_item_id) + 1
    held_pile_tab = game_canvas.held_pile_tab
    assert card_item_id == held_pile_item_ids[-1]  # Note: card_item_id is last and already positioned and raised
    for i in range(insertion_index, held_pile_item_ids_count - 1):
        held_pile_item_id = held_pile_item_ids[i]
        game_canvas.move(held_pile_item_id, held_pile_tab, 0)
        game_canvas.tag_raise(held_pile_item_id)


def set_card_item_id_face_up(card_item_id: int, face_up: bool, game_canvas: 'GameCanvas'):
    card_id = game_canvas.card_item_ids.index(card_item_id)
    game_canvas.set_card_id_face_up(card_id=card_id, face_up=face_up)


def toggle_discard_pile_item_selected(game_canvas: 'GameCanvas'):
    current_player_id = game_canvas.current_player_id
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    item_tags = game_canvas.get_tags(top_discard_pile_item_id)
    is_drawn = configurations.DRAWN_TAG in item_tags
    card_id = game_canvas.card_item_ids.index(top_discard_pile_item_id)
    dx = -20 * game_canvas.scale_factor
    dy = 20 * game_canvas.scale_factor
    if current_player_id == 0:
        dy = -dy
    if is_drawn:
        dx = -dx
        dy = -dy
    game_canvas.jog_card_id(card_id=card_id, dx=dx, dy=dy)
    if is_drawn:
        game_canvas.dtag(top_discard_pile_item_id, configurations.DRAWN_TAG)
    else:
        game_canvas.addtag_withtag(configurations.DRAWN_TAG, top_discard_pile_item_id)


def toggle_held_pile_item_selected(item: CardItem, game_canvas: 'GameCanvas'):
    if isinstance(item, CardItem):  # don't mess with ghost card
        item_tags = item.get_tags()
        is_selected = configurations.SELECTED_TAG in item_tags
        card_id = item.card_id
        dx = 20 * game_canvas.scale_factor
        dy = -20 * game_canvas.scale_factor
        if is_selected:
            dx = -dx
            dy = -dy
        game_canvas.jog_card_id(card_id=card_id, dx=dx, dy=dy)
        if is_selected:
            game_canvas.dtag(item.item_id, configurations.SELECTED_TAG)
            game_canvas.dtag(item.item_id, configurations.JOGGED_TAG)
        else:
            game_canvas.addtag_withtag(configurations.SELECTED_TAG, item.item_id)
            game_canvas.addtag_withtag(configurations.JOGGED_TAG, item.item_id)


def toggle_stock_pile_item_selected(game_canvas: 'GameCanvas'):
    current_player_id = game_canvas.current_player_id
    top_stock_pile_item_id = game_canvas.get_top_stock_pile_item_id()
    item_tags = game_canvas.get_tags(top_stock_pile_item_id)
    is_drawn = configurations.DRAWN_TAG in item_tags
    card_id = game_canvas.card_item_ids.index(top_stock_pile_item_id)
    game_canvas.flip_card_id(card_id)
    dx = 20 * game_canvas.scale_factor
    dy = 20 * game_canvas.scale_factor
    if current_player_id == 0:
        dy = -dy
    if is_drawn:
        dx = -dx
        dy = -dy
    game_canvas.jog_card_id(card_id=card_id, dx=dx, dy=dy)
    if is_drawn:
        game_canvas.dtag(top_stock_pile_item_id, configurations.DRAWN_TAG)
    else:
        game_canvas.addtag_withtag(configurations.DRAWN_TAG, top_stock_pile_item_id)
