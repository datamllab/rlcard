#
#   Gin Rummy
#

import tkinter as tk

from rlcard.games.gin_rummy.card import Card
from rlcard.envs.ginrummy import GinRummyEnv

from .player_type import PlayerType
from ..gui_cards.card_image import CardImage, BetterCardBackImage

from typing import List

from .canvas_item import CardItem, CanvasItem
from .env_controller import EnvController

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.handling_tap_to_arrange_held_pile as handling_tap_to_arrange_held_pile
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.post_doing_action as post_doing_action
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.handling_tap as handling_tap
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.query as query
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.utils as utils

is_debug = __debug__


class GameCanvas(tk.Canvas):

    def __init__(self, parent: tk.Frame, window_width, window_height, scale_factor, gin_rummy_env: GinRummyEnv):
        bottom_info_label_height = int(32 * scale_factor)
        canvas_width = window_width
        canvas_height = window_height - bottom_info_label_height
        super().__init__(master=parent, width=window_width, height=window_height, highlightthickness=0)
        self.configure(background=configurations.GAME_BACKGROUND_COLOR)

        # keep list of relevant canvas items
        canvas_items: [CanvasItem] = []

        # card related instance variables
        card_back_image = BetterCardBackImage(scale_factor=scale_factor)
        card_images = []
        card_item_ids: List[int] = []
        card_items: List[CardItem] = []
        for card_id in range(52):
            card = Card.from_card_id(card_id)
            card_image = CardImage(rank=card.rank, suit=card.suit, scale_factor=scale_factor)
            card_images.append(card_image)
            card_item_id = self.create_image((0, -9999), image=card_image, anchor="nw")
            card_item_ids.append(card_item_id)
            self.itemconfigure(card_item_id, state=tk.HIDDEN)
            card_item = CardItem(item_id=card_item_id, card_id=card_id, card_image=card_image, game_canvas=self)
            card_items.append(card_item)
            canvas_items.append(card_item)
        card_width = card_images[0].width()
        card_height = card_images[0].height()

        # positioning information for stock_pile and discard_pile
        stock_pile_indent = card_width * 2
        stock_pile_tab = max(int(1 * scale_factor), 1)  # Note making int
        stock_pile_anchor = (stock_pile_indent, canvas_height / 2 - card_height / 2)
        discard_pile_anchor = (stock_pile_indent + card_width * 1.8, canvas_height / 2 - card_height / 2)

        # positioning information for held_piles
        held_pile_tab = max(int(card_width * 0.47), 1)  # Note making int
        max_held_pile_width = 10 * held_pile_tab + card_width
        north_held_pile_anchor = (canvas_width / 2 - max_held_pile_width / 2,
                                  stock_pile_anchor[1] - card_height * 1.5)
        south_held_pile_anchor = (canvas_width / 2 - max_held_pile_width / 2,
                                  stock_pile_anchor[1] + card_height * 1.5)

        # draw discard_pile_box
        discard_pile_box_left = discard_pile_anchor[0]
        discard_pile_box_top = discard_pile_anchor[1]
        discard_pile_box_right = discard_pile_box_left + card_width
        discard_pile_box_bottom = discard_pile_box_top + card_height
        discard_pile_box_item_id = self.create_rectangle(discard_pile_box_left,
                                                         discard_pile_box_top,
                                                         discard_pile_box_right,
                                                         discard_pile_box_bottom,
                                                         fill="gray")
        discard_pile_box_item = CanvasItem(item_id=discard_pile_box_item_id, game_canvas=self)
        canvas_items.append(discard_pile_box_item)

        # create player_panes
        player_panes = []
        for player_id in range(2):
            left = 0
            right = canvas_width
            top = 0 if player_id == 0 else stock_pile_anchor[1] + card_height
            bottom = stock_pile_anchor[1] if player_id == 0 else canvas_height
            player_pane_id = self.create_rectangle(left, top, right, bottom, width=0)
            player_pane = CanvasItem(item_id=player_pane_id, game_canvas=self)
            canvas_items.append(player_pane)
            player_panes.append(player_pane)

        # create two held_pile ghost card items
        held_pile_ghost_card_items = []
        player_held_pile_anchors = [north_held_pile_anchor, south_held_pile_anchor]
        held_pile_tags = [configurations.NORTH_HELD_PILE_TAG, configurations.SOUTH_HELD_PILE_TAG]
        for player_id in range(2):
            x, y = player_held_pile_anchors[player_id]
            x -= held_pile_tab
            ghost_card_item_id = self.create_rectangle(x, y, x + card_width, y + card_height, width=0, fill='')
            self.itemconfig(ghost_card_item_id, tag=held_pile_tags[player_id])
            ghost_card_item = CanvasItem(item_id=ghost_card_item_id, game_canvas=self)
            canvas_items.append(ghost_card_item)
            held_pile_ghost_card_items.append(ghost_card_item)

        # create bottom info_label
        info_label = tk.Label(self, text="", padx=10 * scale_factor, anchor="w")
        info_label.config(font=(None, int(bottom_info_label_height * 0.6)))
        info_label.place(x=0, y=canvas_height, width=window_width, height=bottom_info_label_height)

        # create knock_button
        knock_button = tk.Button(self, text="Knock", command=self.on_knock)
        knock_button.configure(font=(None, int(card_height * 0.15)))
        knock_button_x = stock_pile_anchor[0] - card_width * 1.5
        knock_button_y = stock_pile_anchor[1] + card_height / 2 - knock_button.winfo_reqheight() / 2
        knock_button.place(x=knock_button_x, y=knock_button_y)
        knock_button_place = knock_button.place_info()  # remember place
        knock_button.place_forget()  # hide button

        # create dead_hand_button
        knock_button_height = knock_button.winfo_reqheight()
        dead_hand_button = tk.Button(self, text="Dead hand", command=self.on_dead_hand)
        dead_hand_button.configure(font=(None, int(card_height * 0.15)))
        dead_hand_button.place(x=knock_button_x, y=knock_button_y + knock_button_height * 1.5)
        dead_hand_button_place = dead_hand_button.place_info()  # remember place
        dead_hand_button.place_forget()  # hide button

        # create score_pad widget
        cell_width = int(120 * scale_factor)
        cell_height = int(50 * scale_factor)
        cell_border_thickness = int(3 * scale_factor)
        cell_dy = int(5 * scale_factor)
        score_pad_widget = tk.Canvas(self, bg='white', highlightthickness=0)
        score_pad_widget.configure(width=2 * cell_width, height=2 * cell_height)
        score_pad_cells = []
        for row in range(2):
            for col in range(2):
                text = ""
                if row == 0:
                    text = ["Me", "You"][col]
                score_pad_cell = tk.Label(score_pad_widget, text=text, padx=0, pady=0, height=0, bg='white')
                score_pad_cell.config(font=("Times", int(cell_height * 0.6)))
                indent = int(30 * scale_factor + (0 if row == 0 else 10 * scale_factor))
                score_pad_cell.place(x=indent + col * cell_width, y=0 if row == 0 else cell_height)
                if row == 1:
                    score_pad_cells.append(score_pad_cell)
        indent_x = 10 * scale_factor
        indent_y = 5 * scale_factor
        score_pad_widget.create_line(indent_x, cell_height - indent_y, 2 * cell_width - indent_x,
                                     cell_height - indent_y, fill='black', width=cell_border_thickness)
        score_pad_widget.create_line(cell_width, cell_dy, cell_width, 2 * cell_height - cell_dy,
                                     fill='black', width=cell_border_thickness)
        score_pad_widget.pack()
        score_pad_widget.place(x=discard_pile_anchor[0] + 3 * card_width,
                               y=stock_pile_anchor[1] + card_height / 2 - cell_height)

        # set left mouse button action for target canvas
        self.bind("<Button-1>", self.on_tap)
        self.bind("<Shift-Button-1>", self.on_tap_to_arrange_held_pile)
        self.bind("<Button-2>", self.on_tap_to_arrange_held_pile)

        #
        canvas_item_by_item_id = {}  # dictionary of item_id to canvas_item with that item_id
        for canvas_item in canvas_items:
            canvas_item_by_item_id[canvas_item.item_id] = canvas_item

        # keep as instance variables
        self.scale_factor = scale_factor
        self.held_pile_tags = held_pile_tags
        self.player_types: List[PlayerType] = [PlayerType.computer_player, PlayerType.human_player]
        self.dealer_id: int = 0
        self.canvas_items = canvas_items
        self.card_back_image = card_back_image
        self.card_images = card_images
        self.card_item_ids = card_item_ids
        self.card_items = card_items
        self.card_width = card_width
        self.card_height = card_height
        self.stock_pile_anchor = stock_pile_anchor
        self.stock_pile_tab = stock_pile_tab
        self.discard_pile_anchor = discard_pile_anchor
        self.discard_pile_tab = stock_pile_tab
        self.discard_pile_box_item = discard_pile_box_item
        self.player_panes = player_panes
        self.player_held_pile_anchors = player_held_pile_anchors
        self.held_pile_tab = held_pile_tab
        self.held_pile_ghost_card_items = held_pile_ghost_card_items
        self.info_label = info_label
        self.knock_button_place = knock_button_place
        self.knock_button = knock_button
        self.dead_hand_button_place = dead_hand_button_place
        self.dead_hand_button = dead_hand_button
        self.score_pad_cells = score_pad_cells
        self.env_controller = EnvController(game_canvas=self, gin_rummy_env=gin_rummy_env)
        self.canvas_item_by_item_id = canvas_item_by_item_id

        self.pack()

    def update_configurations(self):
        self.configure(background=configurations.GAME_BACKGROUND_COLOR)

    #   =========================================
    #   Getters
    #   =========================================

    def get_card_id(self, card_item_id: int) -> int:
        card_id = self.card_item_ids.index(card_item_id)
        return card_id

    def get_tags(self, item) -> List[str]:
        return [] if not item else self.itemcget(item, 'tags')

    def get_top_discard_pile_item_id(self) -> int or None:
        discard_pile_item_ids = self.find_withtag(configurations.DISCARD_PILE_TAG)
        return None if not discard_pile_item_ids else discard_pile_item_ids[-1]

    def get_top_stock_pile_item_id(self) -> int or None:
        stock_pile_item_ids = self.find_withtag(configurations.STOCK_PILE_TAG)
        return None if not stock_pile_item_ids else stock_pile_item_ids[-1]

    def get_held_pile_item_ids(self, player_id: int) -> List[int]:
        assert player_id is not None
        ghost_card_item = self.held_pile_ghost_card_items[player_id]
        held_pile_tag = self.held_pile_tags[player_id]
        held_pile_item_ids = [item_id for item_id in self.find_withtag(held_pile_tag) if item_id != ghost_card_item]
        return held_pile_item_ids

    def get_selected_held_pile_item_ids(self, player_id: int) -> List[int]:
        held_pile_item_ids = self.get_held_pile_item_ids(player_id)
        selected_held_pile_item_ids = [item_id for item_id in self.find_withtag(configurations.SELECTED_TAG)
                                    if item_id in held_pile_item_ids]
        return selected_held_pile_item_ids

    #   =========================================
    #   Command Methods
    #   =========================================

    def on_dead_hand(self):
        post_doing_action.post_do_declare_dead_hand_action(env_controller=self.env_controller)

    def on_knock(self):
        assert not self.is_game_over()
        selected_held_pile_item_ids = self.get_selected_held_pile_item_ids(player_id=self.current_player_id)
        if len(selected_held_pile_item_ids) == 1:
            selected_held_pile_item_id = selected_held_pile_item_ids[0]
            post_doing_action.post_do_knock_action(selected_held_pile_item_id, env_controller=self.env_controller)

    #   =========================================
    #   Utility Methods
    #   =========================================

    def move_loop(self, item_id, to_location, index=0, dx=0, dy=0, completion=None):
        step_size = 10
        time_in_milli_seconds = 10  # need to figure out the relationship between step_size and time_in_milli_seconds
        if index == 0:
            item_location = self.coords(item_id)
            dx = (to_location[0] - item_location[0]) / step_size
            dy = (to_location[1] - item_location[1]) / step_size
        if index == 1:  # Note: need to put 1 rather than 0. Should I just do tag_raise every iteration ???
            self.tag_raise(item_id)
            self.update_idletasks()  # Note: is this necessary ??? Probably not.
        self.move(item_id, dx, dy)
        index += 1
        if index < step_size:
            self.after(time_in_milli_seconds, self.move_loop, item_id, to_location, index, dx, dy, completion)
        else:
            self.coords(item_id, to_location)
            if completion:
                completion()

    #   =========================================
    #   Private Methods
    #   =========================================

    def on_tap(self, event):
        hit_item_ids = self.find_withtag("current")
        if hit_item_ids:
            assert len(hit_item_ids) == 1
            hit_item_id = hit_item_ids[0]
            hit_item = None
            for canvas_item in self.canvas_items:
                if canvas_item.item_id == hit_item_id:
                    hit_item = canvas_item
            if hit_item:
                handling_tap.handle_tap(hit_item=hit_item, event=event, game_canvas=self)

    def on_tap_to_arrange_held_pile(self, event):
        if self.is_game_over():
            return
        # game must not be over
        hit_items_ids = self.find_withtag("current")
        if not hit_items_ids:
            return
        assert len(hit_items_ids) == 1
        hit_item_id = hit_items_ids[0]
        hit_item = None
        for canvas_item in self.canvas_items:
            if canvas_item.item_id == hit_item_id:
                hit_item = canvas_item
        if hit_item:
            hit_item_tags = hit_item.get_tags()
            hit_held_pile_tag = None
            for held_pile_tag in self.held_pile_tags:
                if held_pile_tag in hit_item_tags:
                    hit_held_pile_tag = held_pile_tag
                    break
            if not hit_held_pile_tag:
                return
            # must hit a held_pile
            hitter_id = self.held_pile_tags.index(hit_held_pile_tag)
            if self.player_types[hitter_id] is not PlayerType.human_player:
                return
            # held_pile hit must belong to human player
            must_do_on_tap = False
            if hitter_id == self.current_player_id:
                must_do_on_tap = query.is_top_discard_pile_item_drawn(self) or query.is_top_stock_pile_item_drawn(self)
            if must_do_on_tap:
                # Minor kludge to handle the following situation.
                # The current_player should just tap to combine drawn card with the selected cards.
                # However, I suspect the player will get in the habit of treating this situation as an arrangement.
                self.on_tap(event)
            else:
                handling_tap_to_arrange_held_pile.handle_tap_to_arrange_held_pile(hit_item=hit_item, game_canvas=self)

    def set_card_id_face_up(self, card_id: int, face_up: bool):
        card_image = self.card_images[card_id]
        if card_image.face_up != face_up:
            card_item_id = self.card_item_ids[card_id]
            target_image = self.card_images[card_id] if face_up else self.card_back_image
            self.itemconfig(card_item_id, image=target_image)
            card_image.face_up = face_up

    def flip_card_id(self, card_id: int):
        card_image = self.card_images[card_id]
        card_item_id = self.card_item_ids[card_id]
        card_image.face_up = not card_image.face_up
        target_image = card_image if card_image.face_up else self.card_back_image
        self.itemconfig(card_item_id, image=target_image)

    def jog_card_id(self, card_id: int, dx: float, dy: float):
        # jog card if held by human player (allows computer to not reveal location of selected cards in hand)
        # TODO: configuration option to highlight card rather than jogging it
        card_item_id = self.card_item_ids[card_id]
        card_item_id_tags = self.get_tags(item=card_item_id)
        player_id = 0 if configurations.NORTH_HELD_PILE_TAG in card_item_id_tags else 1
        if self.player_types[player_id] is PlayerType.human_player:
            self.move(card_item_id, dx, dy)

    #   =========================================
    #   Debugging Methods
    #   =========================================

    def card_name(self, card_item_id: int) -> str:
        card_id = self.card_item_ids.index(card_item_id)
        card = Card.from_card_id(card_id=card_id)
        card_name = f"{card}"
        return card_name

    def description(self):
        dealer_id = self.dealer_id
        current_player_id = self.current_player_id
        stock_pile_item_ids = self.find_withtag(configurations.STOCK_PILE_TAG)
        discard_pile_items = self.find_withtag(configurations.DISCARD_PILE_TAG)
        north_held_pile_item_ids = self.get_held_pile_item_ids(player_id=0)
        south_held_pile_item_ids = self.get_held_pile_item_ids(player_id=1)
        lines = []
        lines.append(f"dealer: {utils.player_short_name(dealer_id)}")
        lines.append(f"current_player: {utils.player_short_name(current_player_id)}")
        lines.append(f"north hand: {[self.card_name(card_item_id) for card_item_id in north_held_pile_item_ids]}")
        lines.append(f"stockpile: {[self.card_name(card_item_id) for card_item_id in stock_pile_item_ids]}")
        lines.append(f"discard pile: {[self.card_name(card_item_id) for card_item_id in discard_pile_items]}")
        lines.append(f"south hand: {[self.card_name(card_item_id) for card_item_id in south_held_pile_item_ids]}")
        return "\n".join(lines)

    #   =========================================
    #   New Methods
    #   =========================================

    def is_game_over(self) -> bool:
        return self.env_controller.env.is_over()

    @property
    def current_player_id(self) -> int:
        return self.env_controller.env.get_player_id()

    def stock_pile(self) -> List[int]:
        return [card.card_id for card in self.env_controller.env.game.round.dealer.stock_pile]
