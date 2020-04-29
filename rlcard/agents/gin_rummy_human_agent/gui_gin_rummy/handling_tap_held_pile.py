'''
    Project: Gui Gin Rummy
    File name: handling_tap_held_pile.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError

from .player_type import PlayerType
from .canvas_item import CanvasItem

from . import configurations
from . import info_messaging
from . import utils


def handle_tap_held_pile(hit_item: CanvasItem, game_canvas: 'GameCanvas'):
    hit_item_tags = hit_item.get_tags()
    if game_canvas.held_pile_tags[0] in hit_item_tags:
        player_id = 0
    elif game_canvas.held_pile_tags[1] in hit_item_tags:
        player_id = 1
    else:
        raise GinRummyProgramError("handle_tap_held_pile: unknown held_pile.")
    player_is_human = game_canvas.player_types[player_id] is PlayerType.human_player
    can_draw_from_stock_pile = game_canvas.query.can_draw_from_stock_pile(player_id=player_id)
    can_draw_from_discard_pile = game_canvas.query.can_draw_from_discard_pile(player_id=player_id)
    is_game_over = game_canvas.query.is_game_over()
    if is_game_over:
        pass
    elif game_canvas.query.can_discard_card(player_id=player_id):  # hit_item is source
        if player_is_human:
            utils.toggle_held_pile_item_selected(item=hit_item, game_canvas=game_canvas)
    elif can_draw_from_stock_pile or can_draw_from_discard_pile:  # hit_item is target
        drawn_card_item_id = None
        drawn_card_item_tag = None
        if not drawn_card_item_id and can_draw_from_stock_pile:
            top_stock_pile_item_id = game_canvas.getter.get_top_stock_pile_item_id()
            top_stock_pile_item_tags = game_canvas.getter.get_tags(top_stock_pile_item_id)
            if configurations.DRAWN_TAG in top_stock_pile_item_tags:
                drawn_card_item_id = top_stock_pile_item_id
                drawn_card_item_tag = configurations.STOCK_PILE_TAG
        if not drawn_card_item_id and can_draw_from_discard_pile:
            top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
            top_discard_pile_item_tags = game_canvas.getter.get_tags(top_discard_pile_item_id)
            if configurations.DRAWN_TAG in top_discard_pile_item_tags:
                drawn_card_item_id = top_discard_pile_item_id
                drawn_card_item_tag = configurations.DISCARD_PILE_TAG
        if drawn_card_item_id:
            if player_id == 1:  # remove info_message if south player
                info_messaging.blank_info_message_label(game_canvas=game_canvas)
            game_canvas.post_doing_action.post_do_get_card_action(player_id=player_id,
                                                                  drawn_card_item_id=drawn_card_item_id,
                                                                  hit_item_id=hit_item.item_id,
                                                                  drawn_card_item_tag=drawn_card_item_tag)
        else:
            utils.toggle_held_pile_item_selected(item=hit_item, game_canvas=game_canvas)
    else:
        if player_is_human:
            utils.toggle_held_pile_item_selected(item=hit_item, game_canvas=game_canvas)  # arranging hand
