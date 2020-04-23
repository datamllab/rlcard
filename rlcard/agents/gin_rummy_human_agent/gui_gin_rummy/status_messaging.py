'''
    Project: Gui Gin Rummy
    File name: status_messaging.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from . import configurations
from . import info_messaging
from . import utils

from .configurations import DECLARE_DEAD_HAND_ACTION_ID
from rlcard.games.gin_rummy.game import GinRummyGame


#
#   Show prolog messages
#

def show_prolog_message(player_id: int, legal_actions, game_canvas: 'GameCanvas'):
    game_canvas_moves = game_canvas.getter.get_game_canvas_moves()
    game_canvas_moves_count = len(game_canvas_moves)
    if 0 < game_canvas_moves_count < 3 and player_id == 1:
        info_messaging.show_activate_menus_message(game_canvas=game_canvas)
    if game_canvas.query.can_declare_dead_hand(player_id=player_id):
        _show_get_card_message(player_id=player_id, game_canvas=game_canvas)
    elif game_canvas.query.can_draw_from_stock_pile(player_id=player_id):
        info_messaging.show_pick_up_discard_message(player_id=player_id, game_canvas=game_canvas)
        _show_get_card_message(player_id=player_id, game_canvas=game_canvas)
    elif game_canvas.query.can_gin(player_id=player_id):
        show_put_card_message(player_id=player_id, game_canvas=game_canvas)
    elif game_canvas.query.can_discard_card(player_id=player_id):
        show_put_card_message(player_id=player_id, game_canvas=game_canvas)
    elif game_canvas.query.is_scoring(legal_actions=legal_actions):
        _show_scoring_message(game_canvas=game_canvas)


def show_put_card_message(player_id: int, game_canvas: 'GameCanvas'):
    is_human_player = game_canvas.query.is_human(player_id=player_id)
    player_name = utils.player_name(player_id=player_id)
    if game_canvas.query.is_dead_hand_button_visible():
        game_canvas.dead_hand_button.place_forget()  # hide button
    can_gin = game_canvas.query.can_gin(player_id=player_id)
    can_knock = game_canvas.query.can_knock(player_id=player_id)
    _show_going_out_button(can_gin=can_gin, can_knock=can_knock, player_id=player_id, game_canvas=game_canvas)
    info_messaging.show_arrange_cards_message(player_id=player_id, game_canvas=game_canvas)
    show_status_messages = configurations.SHOW_STATUS_MESSAGES
    if not show_status_messages == "none":
        is_verbose = show_status_messages == "verbose"
        if not is_human_player:
            message = "{} is discarding.".format(player_name)
        else:
            if is_verbose:
                if can_gin:
                    message = "Put card: tap the gin button to go out."
                elif can_knock:
                    prefix_message = "Put card: tap a card in your hand"
                    suffix_message = "tap the discard pile to discard it or tap the knock button to go out."
                    message = "{}; then {}".format(prefix_message, suffix_message)
                else:
                    prefix_message = "Put card: tap a card in your hand"
                    suffix_message = "tap the discard pile to discard it."
                    message = "{}; then {}".format(prefix_message, suffix_message)
            else:
                message = "Put card."
        game_canvas.info_label.configure(text=message)


#
#   Show epilog messages
#

def show_epilog_message_on_declare_dead_hand(game_canvas: 'GameCanvas'):
    game_canvas.info_label.configure(text="")


def show_game_over_message(game: GinRummyGame, game_canvas: 'GameCanvas'):
    move = game.round.move_sheet[-3]
    if move.action.action_id == DECLARE_DEAD_HAND_ACTION_ID:
        dead_hand_declarer = move.player
        if dead_hand_declarer.player_id == 1:
            prefix_message = "You declared the hand dead."
        else:
            prefix_message = "Your opponent declared the hand dead."
    else:
        prefix_message = "The game is over."
    message = "{} Tap the top card of the discard pile to start a new game.".format(prefix_message)
    game_canvas.info_label.configure(text=message)
    info_messaging.show_hide_tips_message(game_canvas=game_canvas)


#
#   private methods
#

def _show_get_card_message(player_id: int, game_canvas: 'GameCanvas'):
    is_human_player = game_canvas.query.is_human(player_id=player_id)
    player_name = utils.player_name(player_id=player_id)
    can_declare_dead_hand = game_canvas.query.can_declare_dead_hand(player_id=player_id)
    if player_id == 1 and can_declare_dead_hand:
        game_canvas.dead_hand_button.place(game_canvas.dead_hand_button_place)  # show button
    show_status_messages = configurations.SHOW_STATUS_MESSAGES
    if not show_status_messages == "none":
        is_verbose = show_status_messages == "verbose"
        if can_declare_dead_hand:
            if game_canvas.current_player_id == 0:
                message = "Your opponent can declare the hand is dead."
            elif not is_human_player:
                message = "You can declare the hand is dead."
            else:
                if is_verbose:
                    message = ("Tap the dead hand button to declare hand is dead. "
                               "Or tap the discard pile to pickup a discard; "
                               "then tap a card in your hand to place it.")
                else:
                    message = "You can declare the hand is dead."
        else:
            if not is_human_player:
                message = "{} is drawing a card.".format(player_name)
            else:
                if is_verbose:
                    message = ("Get card: tap the stockpile to draw a card "
                               "or tap the discard pile to pickup a discard; "
                               "then tap a card in your hand to place it.")
                else:
                    message = "Get card."
        game_canvas.info_label.configure(text=message)


def _show_going_out_button(can_gin: bool, can_knock: bool, player_id: int, game_canvas: 'GameCanvas'):
    if can_gin and player_id == 1:  # note: show gin button only for south player
        game_canvas.going_out_button.configure(text="Gin")
        game_canvas.going_out_button.place(game_canvas.going_out_button_place)  # show button
    elif can_knock and player_id == 1:  # note: show knock button only for south player
        game_canvas.going_out_button.configure(text="Knock")
        game_canvas.going_out_button.place(game_canvas.going_out_button_place)  # show button
    else:
        game_canvas.going_out_button.place_forget()  # hide button


def _show_scoring_message(game_canvas: 'GameCanvas'):
    game_canvas.info_label.configure(text="")
