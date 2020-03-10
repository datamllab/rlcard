#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

import tkinter as tk

import examples.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import examples.gin_rummy_human_agent.gui_gin_rummy.status_messaging as status_messaging
import examples.gin_rummy_human_agent.gui_gin_rummy.utils as utils

from .player_type import PlayerType

is_debug = __debug__


def start_new_game(game_canvas: 'GameCanvas'):
    game_canvas.env_controller.reset()
    env = game_canvas.env_controller.env
    env.game.settings.going_out_deadwood_count = configurations.GOING_OUT_DEADWOOD_COUNT  # Note this
    env.game.settings.max_drawn_card_count = configurations.MAX_DRAWN_CARD_COUNT  # Note this
    state, player_id = env.init_game()
    game_canvas.dealer_id = (player_id + 1) % 2
    if is_debug:
        settings = game_canvas.env_controller.env.game.settings
        settings.print_settings()
    # Gin Rummy Game
    for player_id in range(2):
        game_canvas.score_pad_cells[player_id].configure(text="")
    for card_id in range(52):
        card_item_id = game_canvas.card_item_ids[card_id]
        game_canvas.itemconfigure(card_item_id, tags=[])
    for card_id in range(52):
        card_item_id = game_canvas.card_item_ids[card_id]
        assert not game_canvas.gettags(card_item_id)
    # Deal cards
    for i in range(2):
        player_id = (game_canvas.dealer_id + 1 + i) % 2
        anchor_x, anchor_y = game_canvas.player_held_pile_anchors[player_id]
        face_up = True
        if player_id == 0:
            if not game_canvas.player_types[player_id] is PlayerType.human_player:
                face_up = False
        card_ids = [card.card_id for card in game_canvas.env_controller.env.game.round.players[player_id].hand]
        card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
        for card_id in card_ids:
            card_item_id = game_canvas.card_item_ids[card_id]
            assert not game_canvas.gettags(card_item_id)
            game_canvas.tag_raise(card_item_id)  # note this
            game_canvas.itemconfig(card_item_id, tag=game_canvas.held_pile_tags[player_id])
            game_canvas.set_card_id_face_up(card_id=card_id, face_up=face_up)
            utils.move_to(card_item_id, anchor_x, anchor_y, parent=game_canvas)
            game_canvas.itemconfigure(card_item_id, state=tk.NORMAL)
            anchor_x += game_canvas.held_pile_tab
    # Deal stockpile cards
    stock_pile_x, stock_pile_y = game_canvas.stock_pile_anchor
    stock_pile = game_canvas.stock_pile()
    for card_id in stock_pile:
        card_item_id = game_canvas.card_item_ids[card_id]
        assert not game_canvas.gettags(card_item_id)
        game_canvas.tag_raise(card_item_id)  # note this
        game_canvas.itemconfig(card_item_id, tag=configurations.STOCK_PILE_TAG)
        game_canvas.set_card_id_face_up(card_id=card_id, face_up=False)
        utils.move_to(card_item_id, stock_pile_x, stock_pile_y, parent=game_canvas)
        game_canvas.itemconfigure(card_item_id, state=tk.NORMAL)
        stock_pile_x += game_canvas.stock_pile_tab
    game_canvas.env_controller.did_perform_actions(actions=[])
    status_messaging.show_put_card_message(game_canvas=game_canvas)
    game_canvas.update()  # seems to be needed: scores not cleared if 'new game' chosen from menu with no mouse move
    if is_debug:
        heading = f"===== Gin Rummy state ====="
        print(heading)
        print(f"{game_canvas.description()}")
        print(f"=" * len(heading))
        print("==================================")
        env.print_state(player=1)
