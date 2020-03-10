#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .env_controller import EnvController
    from .game_canvas import GameCanvas

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.query as query

from .configurations import DECLARE_DEAD_HAND_ACTION_ID


#   =========================================
#   Info message Methods
#   =========================================

def show_put_card_message(game_canvas: 'GameCanvas'):
    can_knock = query.can_knock(game_canvas)
    if can_knock:
        game_canvas.knock_button.place(game_canvas.knock_button_place)  # show button
    else:
        game_canvas.knock_button.place_forget()  # hide button
    show_status_messages = configurations.SHOW_STATUS_MESSAGES
    if not show_status_messages == "none":
        is_verbose = show_status_messages == "verbose"
        if game_canvas.current_player_id == 0:
            message = "North is discarding."
        else:
            if is_verbose:
                prefix_message = "Put card: tap a card in your hand"
                if can_knock:
                    suffix_message = "tap the discard pile to discard it or tap the knock button to go out."

                else:
                    suffix_message = "tap the discard pile to discard it."
                message = f"{prefix_message}; then {suffix_message}"
            else:
                message = "Put card."
        game_canvas.info_label.configure(text=message)


def show_get_card_message(game_canvas: 'GameCanvas'):
    can_declare_dead_hand = query.can_declare_dead_hand(game_canvas)
    if can_declare_dead_hand:
        game_canvas.dead_hand_button.place(game_canvas.dead_hand_button_place)  # show button
    else:
        game_canvas.dead_hand_button.place_forget()  # hide button
    show_status_messages = configurations.SHOW_STATUS_MESSAGES
    if not show_status_messages == "none":
        is_verbose = show_status_messages == "verbose"
        if can_declare_dead_hand:
            if game_canvas.current_player_id == 0:
                message = "Your opponent can declare the hand is dead."
            else:
                if is_verbose:
                    message = ("Tap the dead hand button to declare hand is dead. "
                               "Or tap the discard pile to pickup a discard; "
                               "then tap a card in your hand to place it.")
                else:
                    message = "You can declare the hand is dead."
        else:
            if game_canvas.current_player_id == 0:
                message = "North is drawing a card."
            else:
                if is_verbose:
                    message = ("Get card: tap the stockpile to draw a card "
                               "or tap the discard pile to pickup a discard; "
                               "then tap a card in your hand to place it.")
                else:
                    message = "Get card."
        game_canvas.info_label.configure(text=message)


def show_scoring_message(game_canvas: 'GameCanvas'):
    game_canvas.info_label.configure(text="")


def show_game_over_message(env_controller: 'EnvController'):
    move = env_controller.env.game.round.move_sheet[-3]
    if move.action.action_id == DECLARE_DEAD_HAND_ACTION_ID:
        dead_hand_declarer = move.player
        if dead_hand_declarer.player_id == 1:
            prefix_message = "You declared the hand dead."
        else:
            prefix_message = "Your opponent declared the hand dead."
    else:
        prefix_message = "The game is over."
    message = f"{prefix_message} Tap the top card of the discard pile to start a new game."
    env_controller.game_canvas.info_label.configure(text=message)
