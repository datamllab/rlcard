'''
    Project: Gui Gin Rummy
    File name: starting_new_game.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

import tkinter as tk

from ..gin_rummy_human_agent import HumanAgent

from . import configurations
from . import info_messaging
from . import utils

from .env_thread import EnvThread

import rlcard.games.gin_rummy.utils.utils as gin_rummy_utils
from rlcard.games.gin_rummy.utils.gin_rummy_error import GinRummyProgramError


def start_new_game(game_canvas: 'GameCanvas'):
    info_messaging.blank_info_message_label(game_canvas=game_canvas)
    if game_canvas.game_canvas_updater.env_thread and game_canvas.game_canvas_updater.env_thread.is_alive():
        game_canvas.game_canvas_updater.env_thread.stop()  # FIXME: complex stopping of threads; simplify ???
        while game_canvas.game_canvas_updater.env_thread.is_alive() or not game_canvas.game_canvas_updater.is_stopped:
            game_canvas.update()  # yield time to other threads and to main thread
        if game_canvas.game_canvas_updater.env_thread.is_alive():
            raise GinRummyProgramError("env_thread did not stop.")
    _reset_game_canvas(game_canvas=game_canvas)
    # make new gin_rummy_env
    gin_rummy_env = game_canvas.game_app.make_gin_rummy_env()
    gin_rummy_env.game.settings.going_out_deadwood_count = configurations.GOING_OUT_DEADWOOD_COUNT  # Note this
    gin_rummy_env.game.settings.max_drawn_card_count = configurations.MAX_DRAWN_CARD_COUNT  # Note this
    # start thread
    if utils.is_debug():
        south_agent = gin_rummy_env.agents[1]
        if isinstance(south_agent, HumanAgent):
            if south_agent.state is not None:
                raise GinRummyProgramError("south_agent.state must be None.")
            if south_agent.is_choosing_action_id is True:
                raise GinRummyProgramError("south_agent.is_choosing_action_id must be False.")
            if south_agent.chosen_action_id is not None:
                raise GinRummyProgramError("south_agent.chosen_action_id={} must be None.".format(south_agent.chosen_action_id))
    game_canvas.game_canvas_updater.env_thread = EnvThread(gin_rummy_env=gin_rummy_env, game_canvas=game_canvas)
    game_canvas.game_canvas_updater.env_thread.start()  # Note this: start env background thread


def _reset_game_canvas(game_canvas: 'GameCanvas'):
    game_canvas.dealer_id = 0  # Note: has no effect; will be set later to correct value
    game_canvas.game_canvas_updater.pending_human_action_ids = []
    game_canvas.game_canvas_updater.busy_body_id = None
    game_canvas.game_canvas_updater.is_stopped = False
    for player_id in range(2):
        game_canvas.score_pad_cells[player_id].configure(text="")
    for card_id in range(52):
        card_item_id = game_canvas.card_item_ids[card_id]
        game_canvas.itemconfigure(card_item_id, tags=[])
    game_canvas.update()  # seems to be needed: scores not cleared if 'new game' chosen from menu with no mouse move
    if utils.is_debug():
        for card_id in range(52):
            card_item_id = game_canvas.card_item_ids[card_id]
            tags = game_canvas.gettags(card_item_id)
            if tags:
                raise GinRummyProgramError("tags must be None.")


def show_new_game(game_canvas: 'GameCanvas'):
    game = game_canvas.game_canvas_updater.env_thread.gin_rummy_env.game
    game_canvas.dealer_id = game.round.dealer_id
    dealer = game.round.dealer
    shuffled_deck = dealer.shuffled_deck
    # Deal cards to players
    if utils.is_debug():
        for card_id in range(52):
            card_item_id = game_canvas.card_item_ids[card_id]
            tags = game_canvas.gettags(card_item_id)
            if tags:
                raise GinRummyProgramError("tags must be None.")
    for i in range(2):
        player_id = (game_canvas.dealer_id + 1 + i) % 2
        anchor_x, anchor_y = game_canvas.player_held_pile_anchors[player_id]
        face_up = True
        # Note: cannot use card_ids = [gin_rummy_utils.get_card_id(card) for card in game.round.players[player_id].hand]
        if not game_canvas.is_treating_as_human(player_id=player_id):
            face_up = False
        if i == 0:
            dealt_cards = list(shuffled_deck[-11:])
        else:
            dealt_cards = list(shuffled_deck[-21:-11])
        card_ids = [gin_rummy_utils.get_card_id(card=card) for card in dealt_cards]
        card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
        for card_id in card_ids:
            card_item_id = game_canvas.card_item_ids[card_id]
            if utils.is_debug() or True:
                tags = game_canvas.gettags(card_item_id)
                if tags:
                    raise GinRummyProgramError("tags must be None.")
            game_canvas.tag_raise(card_item_id)  # note this
            game_canvas.itemconfig(card_item_id, tag=game_canvas.held_pile_tags[player_id])
            utils.set_card_id_face_up(card_id=card_id, face_up=face_up, game_canvas=game_canvas)
            utils.move_to(card_item_id, anchor_x, anchor_y, parent=game_canvas)
            game_canvas.itemconfigure(card_item_id, state=tk.NORMAL)
            anchor_x += game_canvas.held_pile_tab
    # Deal stockpile cards
    stock_pile_x, stock_pile_y = game_canvas.stock_pile_anchor
    # Note: cannot use stock_pile = [gin_rummy_utils.get_card_id(card) for card in game.round.dealer.stock_pile]
    stock_pile = list(shuffled_deck[:31])
    stock_pile_card_ids = [gin_rummy_utils.get_card_id(card) for card in stock_pile]
    for card_id in stock_pile_card_ids:
        card_item_id = game_canvas.card_item_ids[card_id]
        if utils.is_debug():
            tags = game_canvas.gettags(card_item_id)
            if tags:
                raise GinRummyProgramError("tags must be None.")
        game_canvas.tag_raise(card_item_id)  # note this
        game_canvas.itemconfig(card_item_id, tag=configurations.STOCK_PILE_TAG)
        utils.set_card_id_face_up(card_id=card_id, face_up=False, game_canvas=game_canvas)
        utils.move_to(card_item_id, stock_pile_x, stock_pile_y, parent=game_canvas)
        game_canvas.itemconfigure(card_item_id, state=tk.NORMAL)
        stock_pile_x += game_canvas.stock_pile_tab
    # update canvas
    game_canvas.update()  # seems to be needed: scores not cleared if 'new game' chosen from menu with no mouse move
    if utils.is_debug():
        settings = game.settings
        settings.print_settings()
