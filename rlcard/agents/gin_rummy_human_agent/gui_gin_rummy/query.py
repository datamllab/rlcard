#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
from .player_type import PlayerType


def is_human(player_id: int, game_canvas: 'GameCanvas') -> bool:
    return  game_canvas.player_types[player_id] is PlayerType.human_player


def is_discard_action(action: int) -> bool:
    discard_action_id = configurations.DISCARD_ACTION_ID
    return discard_action_id <= action < discard_action_id + 52


def is_knock_action(action: int) -> bool:
    knock_action_id = configurations.KNOCK_ACTION_ID
    return knock_action_id <= action < knock_action_id + 52


def can_draw_from_stock_pile(game_canvas: 'GameCanvas') -> bool:
    return configurations.DRAW_CARD_ACTION_ID in game_canvas.env_controller.legal_actions


def can_draw_from_discard_pile(game_canvas: 'GameCanvas') -> bool:
    return configurations.PICK_UP_DISCARD_ACTION_ID in game_canvas.env_controller.legal_actions


def can_declare_dead_hand(game_canvas: 'GameCanvas') -> bool:
    return configurations.DECLARE_DEAD_HAND_ACTION_ID in game_canvas.env_controller.legal_actions


def can_discard_card(game_canvas: 'GameCanvas') -> bool:
    legal_actions = game_canvas.env_controller.legal_actions
    discard_actions = [action for action in legal_actions if is_discard_action(action)]
    return len(discard_actions) > 0


def can_knock(game_canvas: 'GameCanvas') -> bool:
    legal_actions = game_canvas.env_controller.legal_actions
    knock_actions = [action for action in legal_actions if is_knock_action(action)]
    return len(knock_actions) > 0


def is_top_discard_pile_item_drawn(game_canvas: 'GameCanvas') -> bool:
    result = False
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    if top_discard_pile_item_id:
        result = configurations.DRAWN_TAG in game_canvas.get_tags(top_discard_pile_item_id)
    return result


def is_top_stock_pile_item_drawn(game_canvas: 'GameCanvas') -> bool:
    result = False
    top_stock_pile_item_id = game_canvas.get_top_stock_pile_item_id()
    if top_stock_pile_item_id:
        result = configurations.DRAWN_TAG in game_canvas.get_tags(top_stock_pile_item_id)
    return result


def is_item_selected(game_canvas: 'GameCanvas', item) -> bool:
    item_tags = game_canvas.get_tags(item)
    return configurations.SELECTED_TAG in item_tags
