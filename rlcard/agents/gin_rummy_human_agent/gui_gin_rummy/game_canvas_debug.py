'''
    Project: Gui Gin Rummy
    File name: game_canvas_debug.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from . import configurations

from rlcard.games.gin_rummy.player import GinRummyPlayer

import rlcard.games.gin_rummy.utils.utils as gin_rummy_utils


class GameCanvasDebug(object):

    def __init__(self, game_canvas: 'GameCanvas'):
        self.game_canvas = game_canvas

    def get_card_name(self, card_item_id: int) -> str:
        card_id = self.game_canvas.card_item_ids.index(card_item_id)
        card = gin_rummy_utils.card_from_card_id(card_id=card_id)
        return str(card)

    def description(self):
        game_canvas = self.game_canvas
        card_name = self.get_card_name
        dealer_id = game_canvas.dealer_id
        current_player_id = game_canvas.current_player_id
        stock_pile_item_ids = game_canvas.find_withtag(configurations.STOCK_PILE_TAG)
        discard_pile_items = game_canvas.find_withtag(configurations.DISCARD_PILE_TAG)
        north_held_pile_item_ids = game_canvas.getter.get_held_pile_item_ids(player_id=0)
        south_held_pile_item_ids = game_canvas.getter.get_held_pile_item_ids(player_id=1)
        lines = []
        lines.append("dealer: {}".format(GinRummyPlayer.short_name_of(player_id=dealer_id)))
        lines.append("current_player: {}".format(GinRummyPlayer.short_name_of(player_id=current_player_id)))
        lines.append("north hand: {}".format([card_name(card_item_id) for card_item_id in north_held_pile_item_ids]))
        lines.append("stockpile: {}".format([card_name(card_item_id) for card_item_id in stock_pile_item_ids]))
        lines.append("discard pile: {}".format([card_name(card_item_id) for card_item_id in discard_pile_items]))
        lines.append("south hand: {}".format([card_name(card_item_id) for card_item_id in south_held_pile_item_ids]))
        return "\n".join(lines)
