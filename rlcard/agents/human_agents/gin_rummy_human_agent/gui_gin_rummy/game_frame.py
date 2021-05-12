'''
    Project: Gui Gin Rummy
    File name: game_frame.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_app import GameApp

import tkinter as tk

from . import configurations
from . import starting_new_game
from . import utils

from .game_canvas import GameCanvas


class GameFrame(tk.Frame):

    def __init__(self, root: tk.Tk, game_app: 'GameApp'):
        # Set window_title.
        window_title = "Gin Rummy"
        # Set base size.
        # Only the aspect ratio matters for frame size.
        base_height = 750  # type: int
        base_width = 1000  # type: int
        # Set scale_factor_multiplier.
        #   You can change scale_factor_multiplier to increase or decrease the size of the cards,
        #   leaving the size of the the frame the same.
        scale_factor_multiplier = 1.5  # type: float  # Note this: change to scale card size

        preference_window_size_factor = configurations.WINDOW_SIZE_FACTOR
        try:
            window_size_factor = preference_window_size_factor / 100  # type: float
        except ValueError:
            window_size_factor = 0.75  # type: float

        # Get working screen size.
        screenheight_fudge_factor = 0.9  # type: float  # take into account space used by system menus, task bars, etc
        screenwidth = root.winfo_screenwidth()  # screen's width in pixels
        screenheight = root.winfo_screenheight()  # screen's height in pixels
        working_screen_width = int(screenwidth)  # type: int
        working_screen_height = int(screenheight * screenheight_fudge_factor)

        # Determine max frame size.
        min_ratio = min(working_screen_width / base_width, working_screen_height / base_height)  # type: float
        max_frame_width = base_width * min_ratio
        max_frame_height = base_height * min_ratio

        # Determine window rectangle.
        window_width = int(max_frame_width * window_size_factor)  # type: int
        window_height = int(max_frame_height * window_size_factor)  # type: int
        window_x = int((working_screen_width - window_width) / 2)  # type: int
        window_y = int((working_screen_height - window_height) / 2)  # type: int

        super().__init__(root, width=window_width, height=window_height)

        # Set up frame.
        self.root = root
        self.root.title(window_title)
        self.window_size_factor = max(min(window_size_factor, 1), 0.5)
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, window_x, window_y))

        # Set scale_factor for card size.
        self.scale_factor = scale_factor_multiplier * window_size_factor  # type: float

        # Create canvas.
        self.game_canvas = GameCanvas(parent=self, window_width=window_width,
                                      window_height=window_height,
                                      scale_factor=self.scale_factor,
                                      game_app=game_app)
        self.pack()
        self.start_new_game()

        if utils.is_debug():
            self.update()
            print("screen size is {}x{}".format(screenwidth, screenheight))
            print("working screen size is {}x{}".format(working_screen_width, working_screen_height))
            print("(base_width, base_height) is ({}, {})".format(base_width, base_height))
            print("(window_width, window_height) is ({}, {})".format(window_width, window_height))
            print("window size is ({}, {})".format(self.winfo_width(), self.winfo_height()))
            print("window_size_factor={}".format(window_size_factor))
            print("scale_factor={}".format(self.scale_factor))

    def start_new_game(self):
        starting_new_game.start_new_game(game_canvas=self.game_canvas)

    def update_configurations(self):
        self.game_canvas.update_configurations()

    def update_configuration_game_background_color(self, background_color):
        self.game_canvas.update_configuration_game_background_color(background_color=background_color)
