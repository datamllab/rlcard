'''
    Project: Gui Gin Rummy
    File name: info_messaging.py
    Author: William Hale
    Date created: 3/28/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from typing import List

import rlcard.games.gin_rummy.utils.utils as gin_rummy_utils

from rlcard.games.gin_rummy.utils.thinker import Thinker
from .canvas_item import CardItem
from . import configurations


def blank_info_message_label(game_canvas: 'GameCanvas'):
    game_canvas.info_message_label.configure(text="")


def show_activate_menus_message(game_canvas: 'GameCanvas'):
    if not game_canvas.query.is_human(player_id=1):
        return
    if not configurations.IS_SHOW_TIPS:
        return
    if game_canvas.query.is_going_out_button_visible():
        return
    lines = []  # type: List[str]
    lines.append("The menu items may not drop down.")
    lines.append("On an Apple computer, this is a known problem.")
    lines.append("A workaround is to hit cmd-tab twice to switch to another application and back to this application.")
    info_message = " ".join(lines)
    game_canvas.info_message_label.configure(text=info_message)


def show_pick_up_discard_message(player_id: int, game_canvas: 'GameCanvas'):
    if not game_canvas.query.is_human(player_id=1):
        return
    if not configurations.IS_SHOW_TIPS:
        return
    if player_id == 1 and game_canvas.info_message_label['text'] == "":
        hand = game_canvas.getter.get_held_pile_cards(player_id=player_id)
        discard_card_item_id = game_canvas.getter.get_top_discard_pile_item_id()
        discard_card_item = game_canvas.canvas_item_by_item_id[discard_card_item_id]
        if isinstance(discard_card_item, CardItem):
            discard_card_id = discard_card_item.card_id
            discard_card = gin_rummy_utils.get_card(card_id=discard_card_id)
            thinker = Thinker(hand=hand)
            meld_piles_with_discard_card = thinker.get_meld_piles_with_discard_card(discard_card=discard_card)
            if meld_piles_with_discard_card:
                one_meld_pile = meld_piles_with_discard_card[0]
                left_held_card = hand[0]
                if left_held_card not in one_meld_pile:
                    lines = ["Tip:"]  # type: List[str]
                    for card in meld_piles_with_discard_card[0]:
                        if card != discard_card:
                            message = "Tap {} to select it.".format(card)
                            lines.append(message)
                    lines.append("Tap {} to pick it up.".format(discard_card))
                    lines.append("Tap to the left of the {} to drop the new meld.".format(left_held_card))
                    info_message = "\n".join(lines)
                    game_canvas.info_message_label.configure(text=info_message)


def show_arrange_cards_message(player_id: int, game_canvas: 'GameCanvas'):
    if not game_canvas.query.is_human(player_id=1):
        return
    if not configurations.IS_SHOW_TIPS:
        return
    if game_canvas.query.is_going_out_button_visible():
        return
    game_round = game_canvas.query.get_game().round
    if game_round is None:
        return
    move_count = len(game_round.move_sheet)
    if move_count <= 1 or move_count > 8:
        return
    if player_id == 1 and game_canvas.info_message_label['text'] == "":
        lines = ["Tip:"]  # type: List[str]
        lines.append("You can arrange cards in your hand.")
        lines.append("Select the cards you want to move by tapping them.")
        lines.append("Right click the card that you want to drop them on.")
        info_message = " ".join(lines)
        game_canvas.info_message_label.configure(text=info_message)


def show_hide_tips_message(game_canvas: 'GameCanvas'):
    if not game_canvas.query.is_human(player_id=1):
        return
    if not configurations.IS_SHOW_TIPS:
        return
    lines = ["Tip:"]  # type: List[str]
    lines.append("Uncheck 'show tips' in the preferences to hide tips.")
    info_message = " ".join(lines)
    game_canvas.info_message_label.configure(text=info_message)
