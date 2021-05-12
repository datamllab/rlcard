'''
    Project: Gui Gin Rummy
    File name: canvas_item.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.game_canvas import GameCanvas
    from rlcard.agents.gin_rummy_human_agent.gui_cards.card_image import CardImage


class CanvasItem(object):

    def __init__(self, item_id: int, game_canvas: 'GameCanvas'):
        self.item_id = item_id
        self.game_canvas = game_canvas

    def __eq__(self, other):
        if isinstance(other, int):  # FIXME: temporary kludge to convert all item_id to CanvasItem
            return other == self.item_id
        return isinstance(other, CanvasItem) and self.item_id == other.item_id

    def __hash__(self):
        return hash(self.item_id)

    def get_tags(self):
        return self.game_canvas.gettags(self.item_id)


class CardItem(CanvasItem):

    def __init__(self, item_id: int, card_id: int, card_image: 'CardImage', game_canvas: 'GameCanvas'):
        super().__init__(item_id=item_id, game_canvas=game_canvas)
        self.card_id = card_id
        self.card_image = card_image

    def is_face_up(self) -> bool:
        return self.card_image.face_up

    def set_card_id_face_up(self, face_up: bool):
        if self.card_image.face_up != face_up:
            target_image = self.card_image if face_up else self.game_canvas.card_back_image
            self.game_canvas.itemconfig(self.item_id, image=target_image)
            self.card_image.face_up = face_up

    def flip_over(self):
        self.card_image.face_up = not self.card_image.face_up
        target_image = self.card_image if self.card_image.face_up else self.game_canvas.card_back_image
        self.game_canvas.itemconfig(self.item_id, image=target_image)
