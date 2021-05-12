'''
    Project: Gui Gin Rummy
    File name: game_canvas_post_doing_action.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from typing import List, Tuple

from rlcard.games.base import Card

import rlcard.games.gin_rummy.judge as judge
import rlcard.games.gin_rummy.utils.utils as gin_rummy_utils

from rlcard.games.gin_rummy.utils.melding import get_best_meld_clusters

from . import configurations
from . import status_messaging
from . import utils

from .configurations import DRAW_CARD_ACTION_ID, PICK_UP_DISCARD_ACTION_ID
from .configurations import DISCARD_ACTION_ID, KNOCK_ACTION_ID, GIN_ACTION_ID


class GameCanvasPostDoingAction(object):

    def __init__(self, game_canvas: 'GameCanvas'):
        self.game_canvas = game_canvas

    def post_do_get_card_action(self,
                                player_id: int,
                                drawn_card_item_id: int,
                                hit_item_id: int,
                                drawn_card_item_tag: int):
        game_canvas = self.game_canvas
        drawn_card_id = game_canvas.getter.get_card_id(card_item_id=drawn_card_item_id)
        drawn_card = game_canvas.card_items[drawn_card_id]
        if not drawn_card.is_face_up() and game_canvas.is_treating_as_human(player_id=player_id):
            drawn_card.set_card_id_face_up(face_up=True)
        selected_held_pile_item_ids = game_canvas.getter.get_selected_held_pile_item_ids(player_id=player_id)
        if selected_held_pile_item_ids:
            item_ids = selected_held_pile_item_ids + [drawn_card_item_id]
            utils.drop_item_ids(item_ids=item_ids, on_item_id=hit_item_id,
                                player_id=player_id, game_canvas=game_canvas)
            status_messaging.show_put_card_message(player_id=player_id, game_canvas=game_canvas)
            if drawn_card_item_tag == configurations.DISCARD_PILE_TAG:
                action = PICK_UP_DISCARD_ACTION_ID
            else:
                action = DRAW_CARD_ACTION_ID
            game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, [action])
        else:
            to_location = game_canvas.bbox(hit_item_id)[:2]
            dx = game_canvas.held_pile_tab
            to_location = utils.translated_by(dx=dx, dy=0, location=to_location)

            def loop_completion():
                game_canvas.dtag(drawn_card_item_id, configurations.DRAWN_TAG)
                game_canvas.dtag(drawn_card_item_id, drawn_card_item_tag)
                game_canvas.addtag_withtag(game_canvas.held_pile_tags[player_id], drawn_card_item_id)
                if not game_canvas.is_treating_as_human(player_id=player_id):
                    utils.set_card_item_id_face_up(card_item_id=drawn_card_item_id,
                                                   face_up=False,
                                                   game_canvas=game_canvas)
                utils.held_pile_insert(card_item_id=drawn_card_item_id, above_hit_item_id=hit_item_id,
                                       player_id=player_id, game_canvas=game_canvas)
                if drawn_card_item_tag == configurations.DISCARD_PILE_TAG:
                    action = PICK_UP_DISCARD_ACTION_ID
                else:
                    action = DRAW_CARD_ACTION_ID
                game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, [action])

            self._move_loop(drawn_card_item_id, to_location, completion=loop_completion)

    def post_do_discard_action(self, player_id: int, selected_held_pile_item_id: int):
        # The selected held_pile_item is discarded.
        # The remaining held_pile_items are fanned.
        game_canvas = self.game_canvas
        top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
        if top_discard_pile_item_id is None:
            to_location = game_canvas.discard_pile_anchor
        else:
            dx = game_canvas.discard_pile_tab
            to_location = game_canvas.coords(top_discard_pile_item_id)
            to_location = utils.translated_by(dx=dx, dy=0, location=to_location)
        utils.set_card_item_id_face_up(card_item_id=selected_held_pile_item_id, face_up=True, game_canvas=game_canvas)

        if not game_canvas.query.is_human(player_id=player_id):  # turn card over immediately
            selected_card_id = game_canvas.getter.get_card_id(selected_held_pile_item_id)
            utils.set_card_id_face_up(selected_card_id, face_up=True, game_canvas=game_canvas)

        def loop_completion():
            game_canvas.dtag(selected_held_pile_item_id, configurations.SELECTED_TAG)
            game_canvas.dtag(selected_held_pile_item_id, configurations.JOGGED_TAG)
            game_canvas.dtag(selected_held_pile_item_id, game_canvas.held_pile_tags[player_id])
            game_canvas.addtag_withtag(configurations.DISCARD_PILE_TAG, selected_held_pile_item_id)
            utils.fan_held_pile(player_id=player_id, game_canvas=game_canvas)
            card_id = game_canvas.card_item_ids.index(selected_held_pile_item_id)
            action = DISCARD_ACTION_ID + card_id
            game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, [action])

        self._move_loop(selected_held_pile_item_id, to_location, completion=loop_completion)

    def post_do_discard_card_drawn_from_stock_pile_action(self, top_stock_pile_item_id: int):
        game_canvas = self.game_canvas
        top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()

        dx = game_canvas.discard_pile_tab
        to_location = game_canvas.coords(top_discard_pile_item_id)
        to_location = utils.translated_by(dx=dx, dy=0, location=to_location)

        def loop_completion():
            game_canvas.dtag(top_stock_pile_item_id, configurations.DRAWN_TAG)
            game_canvas.dtag(top_stock_pile_item_id, configurations.STOCK_PILE_TAG)
            game_canvas.addtag_withtag(configurations.DISCARD_PILE_TAG, top_stock_pile_item_id)
            card_id = game_canvas.card_item_ids.index(top_stock_pile_item_id)
            actions = [DRAW_CARD_ACTION_ID, DISCARD_ACTION_ID + card_id]
            game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, actions)

        self._move_loop(top_stock_pile_item_id, to_location, completion=loop_completion)

    def post_do_knock_action(self, selected_held_pile_item_id: int):
        # The selected held_pile_item is discarded.
        # The remaining held_pile_items are fanned.
        game_canvas = self.game_canvas
        game_canvas.going_out_button.place_forget()
        current_player_id = game_canvas.current_player_id
        top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
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
            self._show_meld_piles()
            # submit action to game_canvas_updater
            card_id = game_canvas.card_item_ids.index(selected_held_pile_item_id)
            action = KNOCK_ACTION_ID + card_id
            game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, [action])

        self._move_loop(selected_held_pile_item_id, to_location, completion=loop_completion)

    def post_do_gin_action(self):
        game_canvas = self.game_canvas
        game_canvas.going_out_button.place_forget()
        current_player_id = game_canvas.current_player_id

        current_hand = game_canvas.getter.get_held_pile_cards(player_id=current_player_id)
        going_out_deadwood_count = self.game_canvas.game_canvas_updater.env.game.settings.going_out_deadwood_count
        _, gin_cards = judge.get_going_out_cards(hand=current_hand, going_out_deadwood_count=going_out_deadwood_count)
        card = gin_cards[0]
        card_id = gin_rummy_utils.get_card_id(card=card)
        card_item = game_canvas.card_items[card_id]
        selected_held_pile_item_id = card_item.item_id

        top_discard_pile_item_id = game_canvas.getter.get_top_discard_pile_item_id()
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
            self._show_meld_piles()
            # submit action to game_canvas_updater
            action = GIN_ACTION_ID
            game_canvas.after_idle(game_canvas.game_canvas_updater.did_perform_actions, [action])

        self._move_loop(selected_held_pile_item_id, to_location, completion=loop_completion)

    def post_do_declare_dead_hand_action(self, player_id: int):
        game_canvas = self.game_canvas
        status_messaging.show_epilog_message_on_declare_dead_hand(game_canvas=game_canvas)
        game_canvas.going_out_button.place_forget()
        game_canvas.dead_hand_button.place_forget()
        # show meld piles for both players
        self._show_meld_piles()

    #   =========================================
    #   Private methods
    #   =========================================

    def _show_meld_piles(self):
        game_canvas = self.game_canvas
        current_player_id = game_canvas.current_player_id
        opponent_player_id = (current_player_id + 1) % 2
        utils.fan_held_pile(player_id=current_player_id, game_canvas=game_canvas)
        # do current_player_id melding
        best_meld_cluster = self._get_best_meld_cluster(player_id=current_player_id)
        self.put_down_meld_cluster(best_meld_cluster, player_id=current_player_id)
        # do opponent_player_id melding
        opponent_best_meld_cluster = self._get_best_meld_cluster(player_id=opponent_player_id)
        self.put_down_meld_cluster(opponent_best_meld_cluster, player_id=opponent_player_id)

    def _get_best_meld_cluster(self, player_id: int) -> List[List[Card]]:
        game_canvas = self.game_canvas
        hand = game_canvas.getter.get_held_pile_cards(player_id=player_id)
        best_meld_clusters = get_best_meld_clusters(hand=hand)
        best_meld_cluster = [] if not best_meld_clusters else best_meld_clusters[0]
        return best_meld_cluster

    def put_down_meld_cluster(self, meld_cluster, player_id: int):
        game_canvas = self.game_canvas
        card_width = game_canvas.card_width
        card_height = game_canvas.card_height
        player_pane = game_canvas.player_panes[player_id]
        y_tab = int(card_height * 0.15)
        anchor_x = int(card_width * 0.5)  # type: int
        anchor_y = int(game_canvas.coords(player_pane.item_id)[1]) + y_tab  # type: int
        for meld_pile in meld_cluster:
            self.put_down_meld_pile(meld_pile, anchor=(anchor_x, anchor_y), player_id=player_id)
            utils.fan_held_pile(player_id=player_id, game_canvas=game_canvas)
            anchor_x += len(meld_pile) * game_canvas.held_pile_tab
            anchor_y += y_tab
        held_pile_item_ids = game_canvas.getter.get_held_pile_item_ids(player_id=player_id)
        if not game_canvas.query.is_human(player_id):
            # sort deadwood cards of computer player
            held_pile_cards = game_canvas.getter.get_held_pile_cards(player_id=player_id)
            card_ids = [gin_rummy_utils.get_card_id(card) for card in held_pile_cards]
            sorted_card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
            for sorted_card_id in sorted_card_ids:
                card_item_id = game_canvas.card_item_ids[sorted_card_id]
                game_canvas.tag_raise(card_item_id)
            utils.fan_held_pile(player_id, game_canvas=game_canvas)
            # face up deadwood cards of computer player
            for held_pile_item_id in held_pile_item_ids:
                utils.set_card_item_id_face_up(card_item_id=held_pile_item_id, face_up=True, game_canvas=game_canvas)

    def put_down_meld_pile(self, meld_pile: List[Card], anchor: Tuple[int, int], player_id: int):
        game_canvas = self.game_canvas
        held_pile_tag = game_canvas.held_pile_tags[player_id]
        x, y = anchor
        card_ids = [gin_rummy_utils.get_card_id(card=card) for card in meld_pile]
        sorted_card_ids = sorted(card_ids, reverse=True, key=utils.gin_rummy_sort_order_id)
        for sorted_card_id in sorted_card_ids:
            card_item_id = game_canvas.card_item_ids[sorted_card_id]
            game_canvas.tag_raise(card_item_id)
            game_canvas.dtag(card_item_id, held_pile_tag)
            utils.move_to(card_item_id, x, y, game_canvas)
            utils.set_card_item_id_face_up(card_item_id, face_up=True, game_canvas=game_canvas)
            x += game_canvas.held_pile_tab

    #   =========================================
    #   Utility Methods
    #   =========================================

    def _move_loop(self, item_id, to_location, index=0, dx=0, dy=0, completion=None):
        game_canvas = self.game_canvas
        step_size = 10
        time_in_milli_seconds = 10  # need to figure out the relationship between step_size and time_in_milli_seconds
        if index == 0:
            item_location = game_canvas.coords(item_id)
            dx = (to_location[0] - item_location[0]) / step_size
            dy = (to_location[1] - item_location[1]) / step_size
        if index == 1:  # Note: need to put 1 rather than 0. Should I just do tag_raise every iteration ???
            game_canvas.tag_raise(item_id)
            game_canvas.update_idletasks()  # Note: is this necessary ??? Probably not.
        game_canvas.move(item_id, dx, dy)
        index += 1
        if index < step_size:
            game_canvas.after(time_in_milli_seconds, self._move_loop, item_id, to_location, index, dx, dy, completion)
        else:
            game_canvas.coords(item_id, to_location)
            if completion:
                completion()
