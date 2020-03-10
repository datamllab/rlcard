#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas
    from .env_controller import EnvController

from typing import List, Tuple

import examples.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import examples.gin_rummy_human_agent.gui_gin_rummy.query as query
import examples.gin_rummy_human_agent.gui_gin_rummy.status_messaging as status_messaging
import examples.gin_rummy_human_agent.gui_gin_rummy.utils as utils

from .player_type import PlayerType

from .configurations import SCORE_PLAYER_0_ACTION_ID, SCORE_PLAYER_1_ACTION_ID
from .configurations import DRAW_CARD_ACTION_ID, PICK_UP_DISCARD_ACTION_ID
from .configurations import DISCARD_ACTION_ID, KNOCK_ACTION_ID
from .configurations import DECLARE_DEAD_HAND_ACTION_ID

from rlcard.games.gin_rummy.utils import get_deadwood_value
from rlcard.games.gin_rummy.card import Card
from rlcard.games.gin_rummy.melding import get_best_meld_clusters

is_debug = __debug__


def post_do_score_player_action(env_controller: 'EnvController'):
    game_canvas = env_controller.game_canvas
    current_player_id = game_canvas.current_player_id
    action = SCORE_PLAYER_0_ACTION_ID if current_player_id == 0 else SCORE_PLAYER_1_ACTION_ID
    if action == SCORE_PLAYER_1_ACTION_ID:
        for player_id in range(2):
            held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=player_id)
            held_pile_card_ids = [game_canvas.get_card_id(card_item_id=item_id) for item_id in held_pile_item_ids]
            held_pile_cards = [Card.from_card_id(card_id) for card_id in held_pile_card_ids]
            deadwood_count = sum([get_deadwood_value(card) for card in held_pile_cards])
            text = f"{deadwood_count}"
            game_canvas.score_pad_cells[player_id].configure(text=text)
    game_canvas.after_idle(env_controller.did_perform_actions, [action])


def post_do_get_card_action(drawn_card_item_id: int,
                            hit_item_id: int,
                            drawn_card_item_tag: int,
                            env_controller: 'EnvController'):
    game_canvas = env_controller.game_canvas
    current_player_id = game_canvas.current_player_id
    selected_held_pile_item_ids = game_canvas.get_selected_held_pile_item_ids(player_id=current_player_id)
    if selected_held_pile_item_ids:
        item_ids = selected_held_pile_item_ids + [drawn_card_item_id]
        utils.drop_item_ids(item_ids=item_ids, on_item_id=hit_item_id,
                            player_id=current_player_id, game_canvas=game_canvas)
        status_messaging.show_put_card_message(game_canvas=game_canvas)
        if drawn_card_item_tag == configurations.DISCARD_PILE_TAG:
            action = PICK_UP_DISCARD_ACTION_ID
        else:
            action = DRAW_CARD_ACTION_ID
        game_canvas.after_idle(env_controller.did_perform_actions, [action])
    else:
        to_location = game_canvas.bbox(hit_item_id)[:2]
        dx = game_canvas.held_pile_tab
        to_location = utils.translated_by(dx=dx, dy=0, location=to_location)

        def loop_completion():
            game_canvas.dtag(drawn_card_item_id, configurations.DRAWN_TAG)
            game_canvas.dtag(drawn_card_item_id, drawn_card_item_tag)
            game_canvas.addtag_withtag(game_canvas.held_pile_tags[current_player_id], drawn_card_item_id)
            if game_canvas.player_types[current_player_id] == PlayerType.computer_player:
                utils.set_card_item_id_face_up(card_item_id=drawn_card_item_id, face_up=False, game_canvas=game_canvas)
            utils.held_pile_insert(card_item_id=drawn_card_item_id, above_card_item_id=hit_item_id,
                                   player_id=current_player_id, game_canvas=game_canvas)
            if drawn_card_item_tag == configurations.DISCARD_PILE_TAG:
                action = PICK_UP_DISCARD_ACTION_ID
            else:
                action = DRAW_CARD_ACTION_ID
            game_canvas.after_idle(env_controller.did_perform_actions, [action])

        game_canvas.move_loop(drawn_card_item_id, to_location, completion=loop_completion)


def post_do_discard_action(selected_held_pile_item_id: int, env_controller: 'EnvController'):
    # The selected held_pile_item is discarded.
    # The remaining held_pile_items are fanned.
    game_canvas = env_controller.game_canvas
    current_player_id = game_canvas.current_player_id
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    if top_discard_pile_item_id is None:
        to_location = game_canvas.discard_pile_anchor
    else:
        dx = game_canvas.discard_pile_tab
        to_location = game_canvas.coords(top_discard_pile_item_id)
        to_location = utils.translated_by(dx=dx, dy=0, location=to_location)
    utils.set_card_item_id_face_up(card_item_id=selected_held_pile_item_id, face_up=True, game_canvas=game_canvas)

    def loop_completion():
        game_canvas.dtag(selected_held_pile_item_id, configurations.SELECTED_TAG)
        game_canvas.dtag(selected_held_pile_item_id, configurations.JOGGED_TAG)
        game_canvas.dtag(selected_held_pile_item_id, game_canvas.held_pile_tags[current_player_id])
        game_canvas.addtag_withtag(configurations.DISCARD_PILE_TAG, selected_held_pile_item_id)
        utils.fan_held_pile(player_id=current_player_id, game_canvas=game_canvas)
        card_id = game_canvas.card_item_ids.index(selected_held_pile_item_id)
        action = DISCARD_ACTION_ID + card_id
        game_canvas.after_idle(env_controller.did_perform_actions, [action])

    game_canvas.move_loop(selected_held_pile_item_id, to_location, completion=loop_completion)


def post_do_discard_card_drawn_from_stock_pile_action(top_stock_pile_item_id: int, env_controller: 'EnvController'):
    game_canvas = env_controller.game_canvas
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()

    dx = game_canvas.discard_pile_tab
    to_location = game_canvas.coords(top_discard_pile_item_id)
    to_location = utils.translated_by(dx=dx, dy=0, location=to_location)

    def loop_completion():
        game_canvas.dtag(top_stock_pile_item_id, configurations.DRAWN_TAG)
        game_canvas.dtag(top_stock_pile_item_id, configurations.STOCK_PILE_TAG)
        game_canvas.addtag_withtag(configurations.DISCARD_PILE_TAG, top_stock_pile_item_id)
        card_id = game_canvas.card_item_ids.index(top_stock_pile_item_id)
        actions = [DRAW_CARD_ACTION_ID, DISCARD_ACTION_ID + card_id]
        game_canvas.after_idle(env_controller.did_perform_actions, actions)

    game_canvas.move_loop(top_stock_pile_item_id, to_location, completion=loop_completion)


def post_do_knock_action(selected_held_pile_item_id: int, env_controller: 'EnvController'):
    # The selected held_pile_item is discarded.
    # The remaining held_pile_items are fanned.
    game_canvas = env_controller.game_canvas
    game_canvas.knock_button.place_forget()
    game_canvas.dead_hand_button.place_forget()
    current_player_id = game_canvas.current_player_id
    opponent_player_id = (current_player_id + 1) % 2
    top_discard_pile_item_id = game_canvas.get_top_discard_pile_item_id()
    if top_discard_pile_item_id is None:
        to_location = game_canvas.discard_pile_anchor
    else:
        dx = game_canvas.discard_pile_tab
        to_location = game_canvas.coords(top_discard_pile_item_id)
        to_location = utils.translated_by(dx=dx, dy=0, location=to_location)
    utils.set_card_item_id_face_up(card_item_id=selected_held_pile_item_id, face_up=True, game_canvas=game_canvas)

    def loop_completion():
        game_canvas.dtag(selected_held_pile_item_id, configurations.SELECTED_TAG)
        game_canvas.dtag(selected_held_pile_item_id, configurations.JOGGED_TAG)
        game_canvas.dtag(selected_held_pile_item_id, game_canvas.held_pile_tags[current_player_id])
        game_canvas.addtag_withtag(configurations.DISCARD_PILE_TAG, selected_held_pile_item_id)
        utils.fan_held_pile(player_id=current_player_id, game_canvas=game_canvas)
        # show meld piles for both players
        show_meld_piles(env_controller=env_controller)
        # submit action to env_controller
        card_id = game_canvas.card_item_ids.index(selected_held_pile_item_id)
        action = KNOCK_ACTION_ID + card_id
        game_canvas.after_idle(env_controller.did_perform_actions, [action])

    game_canvas.move_loop(selected_held_pile_item_id, to_location, completion=loop_completion)


def post_do_declare_dead_hand_action(env_controller: 'EnvController'):
    game_canvas = env_controller.game_canvas
    game_canvas.knock_button.place_forget()
    game_canvas.dead_hand_button.place_forget()
    # show meld piles for both players
    show_meld_piles(env_controller=env_controller)
    # submit action to env_controller
    game_canvas.after_idle(env_controller.did_perform_actions, [DECLARE_DEAD_HAND_ACTION_ID])


#
#   Private methods
#

def show_meld_piles(env_controller: 'EnvController'):
    game_canvas = env_controller.game_canvas
    current_player_id = game_canvas.current_player_id
    opponent_player_id = (current_player_id + 1) % 2
    utils.fan_held_pile(player_id=current_player_id, game_canvas=game_canvas)
    # do current_player_id melding
    best_meld_cluster = get_best_meld_cluster(player_id=current_player_id, game_canvas=game_canvas)
    put_down_meld_cluster(best_meld_cluster, player_id=current_player_id, game_canvas=game_canvas)
    # do opponent_player_id melding
    opponent_best_meld_cluster = get_best_meld_cluster(player_id=opponent_player_id, game_canvas=game_canvas)
    put_down_meld_cluster(opponent_best_meld_cluster, player_id=opponent_player_id, game_canvas=game_canvas)


def get_best_meld_cluster(player_id: int, game_canvas: 'GameCanvas') -> List[List[Card]]:
    held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=player_id)
    held_card_ids = [game_canvas.get_card_id(item_id) for item_id in held_pile_item_ids]
    hand = [Card.from_card_id(card_id=card_id) for card_id in held_card_ids]
    best_meld_clusters = get_best_meld_clusters(hand=hand)
    best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
    return best_meld_cluster


def put_down_meld_cluster(meld_cluster, player_id: int, game_canvas: 'GameCanvas'):
    card_width = game_canvas.card_width
    card_height = game_canvas.card_height
    player_pane = game_canvas.player_panes[player_id]
    y_tab = int(card_height * 0.15)
    anchor_x: int = int(card_width * 0.5)
    anchor_y: int = int(game_canvas.coords(player_pane.item_id)[1]) + y_tab
    for index in range(len(meld_cluster)):
        meld_pile = meld_cluster[index]
        put_down_meld_pile(meld_pile, anchor=(anchor_x, anchor_y), player_id=player_id, game_canvas=game_canvas)
        utils.fan_held_pile(player_id=player_id, game_canvas=game_canvas)
        anchor_x += len(meld_pile) * game_canvas.held_pile_tab
        anchor_y += y_tab
    held_pile_item_ids = game_canvas.get_held_pile_item_ids(player_id=player_id)
    if not query.is_human(player_id, game_canvas=game_canvas):
        # sort deadwood cards of computer player
        card_ids = [game_canvas.get_card_id(item_id) for item_id in held_pile_item_ids]
        sorted_card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
        for sorted_card_id in sorted_card_ids:
            card_item_id = game_canvas.card_item_ids[sorted_card_id]
            game_canvas.tag_raise(card_item_id)
        utils.fan_held_pile(player_id, game_canvas=game_canvas)
        # face up deadwood cards of computer player
        for held_pile_item_id in held_pile_item_ids:
            utils.set_card_item_id_face_up(card_item_id=held_pile_item_id, face_up=True, game_canvas=game_canvas)


def put_down_meld_pile(meld_pile: List[Card], anchor: Tuple[int, int], player_id: int, game_canvas: 'GameCanvas'):
    held_pile_tag = game_canvas.held_pile_tags[player_id]
    x, y = anchor
    card_ids = [card.card_id for card in meld_pile]
    sorted_card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
    for sorted_card_id in sorted_card_ids:
        card_item_id = game_canvas.card_item_ids[sorted_card_id]
        game_canvas.tag_raise(card_item_id)
        game_canvas.dtag(card_item_id, held_pile_tag)
        utils.move_to(card_item_id, x, y, game_canvas)
        utils.set_card_item_id_face_up(card_item_id, face_up=True, game_canvas=game_canvas)
        x += game_canvas.held_pile_tab
