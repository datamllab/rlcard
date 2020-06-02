'''
    Project: Gui Gin Rummy
    File name: game_canvas.query.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_canvas import GameCanvas

from typing import List

from rlcard.games.gin_rummy.game import GinRummyGame

from rlcard.games.gin_rummy.utils.action_event import DrawCardAction, PickUpDiscardAction, DeclareDeadHandAction
from rlcard.games.gin_rummy.utils.action_event import DiscardAction, KnockAction, GinAction
from rlcard.games.gin_rummy.utils.move import ScoreSouthMove

from . import configurations

from .configurations import SCORE_PLAYER_0_ACTION_ID, SCORE_PLAYER_1_ACTION_ID
from .player_type import PlayerType


class GameCanvasQuery(object):

    def __init__(self, game_canvas: 'GameCanvas'):
        self.game_canvas = game_canvas

    def get_game(self) -> GinRummyGame:
        return self.game_canvas.game_canvas_updater.env_thread.gin_rummy_env.game

    def is_game_over(self) -> bool:
        result = False
        game = self.get_game()
        mark = self.game_canvas.game_canvas_updater.mark
        if game.round:
            moves = game.round.move_sheet[:mark]
            if moves:
                last_move = moves[-1]
                result = isinstance(last_move, ScoreSouthMove)
        return result

    def is_human(self, player_id: int or None) -> bool:
        return False if player_id is None else self.game_canvas.player_types[player_id] is PlayerType.human_player

    def is_dead_hand_button_visible(self):
        return self.game_canvas.dead_hand_button.place_info() != {}

    def is_going_out_button_visible(self):
        return self.game_canvas.going_out_button.place_info() != {}

    def can_draw_from_stock_pile(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        draw_card_actions = [x for x in legal_actions if isinstance(x, DrawCardAction)]
        return len(draw_card_actions) > 0

    def can_draw_from_discard_pile(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        pick_up_discard_actions = [x for x in legal_actions if isinstance(x, PickUpDiscardAction)]
        return len(pick_up_discard_actions) > 0

    def can_declare_dead_hand(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        declare_dead_hand_actions = [x for x in legal_actions if isinstance(x, DeclareDeadHandAction)]
        return len(declare_dead_hand_actions) > 0

    def can_discard_card(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        discard_actions = [action for action in legal_actions if isinstance(action, DiscardAction)]
        return len(discard_actions) > 0

    def can_knock(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        knock_actions = [action for action in legal_actions if isinstance(action, KnockAction)]
        return len(knock_actions) > 0

    def can_gin(self, player_id: int) -> bool:
        legal_actions = self.game_canvas.getter.get_legal_actions(player_id=player_id)
        gin_actions = [action for action in legal_actions if isinstance(action, GinAction)]
        return len(gin_actions) > 0

    def is_top_discard_pile_item_drawn(self) -> bool:
        result = False
        top_discard_pile_item_id = self.game_canvas.getter.get_top_discard_pile_item_id()
        if top_discard_pile_item_id:
            result = configurations.DRAWN_TAG in self.game_canvas.getter.get_tags(top_discard_pile_item_id)
        return result

    def is_top_stock_pile_item_drawn(self) -> bool:
        result = False
        top_stock_pile_item_id = self.game_canvas.getter.get_top_stock_pile_item_id()
        if top_stock_pile_item_id:
            result = configurations.DRAWN_TAG in self.game_canvas.getter.get_tags(top_stock_pile_item_id)
        return result

    def is_item_id_selected(self, item_id) -> bool:
        item_tags = self.game_canvas.getter.get_tags(item_id)
        return configurations.SELECTED_TAG in item_tags

    @staticmethod
    def is_scoring(legal_actions: List[int]) -> bool:
        return SCORE_PLAYER_0_ACTION_ID in legal_actions or SCORE_PLAYER_1_ACTION_ID in legal_actions
