#
#   Gin Rummy
#

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

import random

from rlcard.envs.ginrummy import GinRummyEnv

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.handling_tap_discard_pile as handling_tap_discard_pile
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.handling_tap_held_pile as handling_tap_held_pile
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.post_doing_action as post_doing_action
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.query as query
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.status_messaging as status_messaging
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.utils as utils
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.exceptions as exceptions

from .player_type import PlayerType

from .configurations import SCORE_PLAYER_0_ACTION_ID, SCORE_PLAYER_1_ACTION_ID
from .configurations import DRAW_CARD_ACTION_ID, PICK_UP_DISCARD_ACTION_ID
from .configurations import DECLARE_DEAD_HAND_ACTION_ID
from .configurations import DISCARD_ACTION_ID, KNOCK_ACTION_ID

from typing import List

is_debug = __debug__


class EnvController(object):

    def __init__(self, game_canvas: 'GameCanvas', gin_rummy_env: GinRummyEnv):
        self.game_canvas = game_canvas
        self.env = gin_rummy_env
        self.current_player_id: int or None = None
        self.legal_actions = []

    def reset(self):
        self.current_player_id = None
        self.legal_actions = []

    #   =========================================
    #   Perform env actions
    #   =========================================

    def will_perform_action(self):
        # Everything should be reset after submission of the move to env.
        assert self.current_player_id is None
        assert not self.legal_actions
        is_over = self.env.game.is_over()
        if is_over:
            status_messaging.show_game_over_message(env_controller=self)
        else:
            self.current_player_id = self.env.get_player_id()
            self.legal_actions = self.env._get_legal_actions()
            # show status message
            if query.can_declare_dead_hand(game_canvas=self.game_canvas):
                status_messaging.show_get_card_message(game_canvas=self.game_canvas)
            elif query.can_draw_from_stock_pile(game_canvas=self.game_canvas):
                status_messaging.show_get_card_message(game_canvas=self.game_canvas)
            elif query.can_knock(game_canvas=self.game_canvas):
                status_messaging.show_put_card_message(game_canvas=self.game_canvas)
            elif query.can_discard_card(game_canvas=self.game_canvas):
                status_messaging.show_put_card_message(game_canvas=self.game_canvas)
            elif self._is_scoring():
                status_messaging.show_scoring_message(game_canvas=self.game_canvas)
            if self._is_scoring():
                self.game_canvas.after_idle(self.do_perform_action)
            elif self.game_canvas.player_types[self.current_player_id] == PlayerType.human_player:
                self.game_canvas.after_idle(self.do_perform_action)
            else:
                # simulate the computer thinking
                thinking_time_in_ms: int = 1000
                self.game_canvas.after(thinking_time_in_ms, self.do_perform_action)

    def do_perform_action(self):
        is_human_current_player = self.game_canvas.player_types[self.current_player_id] is PlayerType.human_player
        is_scoring = SCORE_PLAYER_0_ACTION_ID in self.legal_actions or SCORE_PLAYER_1_ACTION_ID in self.legal_actions
        if is_human_current_player and not is_scoring:
            pass
        else:
            action = random.choice(self.legal_actions)  # FIXME: stub
            action_type = utils.get_action_type(action)
            if action_type is DRAW_CARD_ACTION_ID:
                source_item_id = self.game_canvas.get_top_stock_pile_item_id()
                self.game_canvas.addtag_withtag(configurations.DRAWN_TAG, source_item_id)
                target_item_id = self.game_canvas.get_held_pile_item_ids(player_id=self.current_player_id)[-1]
                target_item = self.game_canvas.canvas_item_by_item_id[target_item_id]
                handling_tap_held_pile.handle_tap_held_pile(hit_item=target_item, game_canvas=self.game_canvas)
            elif action_type is PICK_UP_DISCARD_ACTION_ID:
                source_item_id = self.game_canvas.get_top_discard_pile_item_id()
                self.game_canvas.addtag_withtag(configurations.DRAWN_TAG, source_item_id)
                target_item_id = self.game_canvas.get_held_pile_item_ids(player_id=self.current_player_id)[-1]
                target_item = self.game_canvas.canvas_item_by_item_id[target_item_id]
                handling_tap_held_pile.handle_tap_held_pile(hit_item=target_item, game_canvas=self.game_canvas)
            elif action_type is DECLARE_DEAD_HAND_ACTION_ID:
                post_doing_action.post_do_declare_dead_hand_action(env_controller=self)
            elif action_type is DISCARD_ACTION_ID:
                self._do_perform_discard_action(action=action)
            elif action_type is KNOCK_ACTION_ID:
                self._do_perform_knock_action(action=action)
            elif action_type is SCORE_PLAYER_0_ACTION_ID:
                post_doing_action.post_do_score_player_action(env_controller=self)
            elif action_type is SCORE_PLAYER_1_ACTION_ID:
                post_doing_action.post_do_score_player_action(env_controller=self)
            else:
                raise exceptions.ProgramError(f"No action type for action={action}")

    def did_perform_actions(self, actions: List[int]):
        for action in actions:
            self.env.step(action)
            if is_debug:
                action_type = utils.get_action_type(action)
                card_id = utils.get_action_card_id(action)
                suffix = "" if card_id is None else f" card_id={card_id}"
                print(f"action={action} action_type={action_type}{suffix}")
        self.reset()
        self.game_canvas.after_idle(self.will_perform_action)

    #
    #   Private methods
    #

    def _is_scoring(self) -> bool:
        return SCORE_PLAYER_0_ACTION_ID in self.legal_actions or SCORE_PLAYER_1_ACTION_ID in self.legal_actions

    def _do_perform_discard_action(self, action: int):
        current_player_id = self.current_player_id
        assert current_player_id is not None
        card_id = utils.get_action_card_id(action)
        source_item_id = self.game_canvas.card_item_ids[card_id]
        self.game_canvas.addtag_withtag(configurations.SELECTED_TAG, source_item_id)
        target_item_id = self.game_canvas.get_top_discard_pile_item_id()
        if target_item_id is None:
            target_item_id = self.game_canvas.discard_pile_box_item
        if not self.game_canvas.player_types[current_player_id] == PlayerType.computer_player:
            # move source_item_id to end of held_pile invisibly
            self.game_canvas.tag_raise(source_item_id)
            utils.fan_held_pile(player_id=self.current_player_id, game_canvas=self.game_canvas)
        handling_tap_discard_pile.handle_tap_discard_pile(hit_item=target_item_id, game_canvas=self.game_canvas)

    def _do_perform_knock_action(self, action: int):
        print(f"_do_perform_knock_action")
        card_id = utils.get_action_card_id(action)
        source_item_id = self.game_canvas.card_item_ids[card_id]
        self.game_canvas.addtag_withtag(configurations.SELECTED_TAG, source_item_id)
        post_doing_action.post_do_knock_action(source_item_id, env_controller=self)
