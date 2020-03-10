#
#   Gin Rummy
#

import tkinter as tk

from rlcard.envs.ginrummy import GinRummyEnv

from .game_canvas import GameCanvas

import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.configurations as configurations
import rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.starting_new_game as starting_new_game

is_debug = __debug__


class GameFrame(tk.Frame):

    def __init__(self, root: tk.Tk, gin_rummy_env: GinRummyEnv):
        super().__init__(root)

        # Set window_title.
        window_title = "Gin Rummy"
        # Set scale_factor_multiplier.
        #   You can change scale_factor_multiplier to increase or decrease the size of the cards,
        #   leaving the size of the the frame the same.
        scale_factor_multiplier: float = 1.5  # Note this: change to scale card size
        # Set base size.
        # Only the aspect ratio matters for frame size.
        base_height = 750
        base_width = 1000

        # Set up frame.
        self.root = root
        self.root.title(window_title)

        preference_window_size_factor = configurations.WINDOW_SIZE_FACTOR
        try:
            window_size_factor = int(preference_window_size_factor) / 100
        except ValueError:
            window_size_factor = 0.75
        self.window_size_factor = max(min(window_size_factor, 1), 0.5)

        # Get working screen size.
        screenheight_fudge_factor: float = 0.9  # take into account space used by system menus, task bars, etc
        screenwidth = self.root.winfo_screenwidth()  # screen's width in pixels
        screenheight = self.root.winfo_screenheight()  # screen's height in pixels
        working_screen_width: int = int(screenwidth)
        working_screen_height = int(screenheight * screenheight_fudge_factor)

        # Determine max frame size.
        min_ratio: float = min(working_screen_width / base_width, working_screen_height / base_height)
        max_frame_width = base_width * min_ratio
        max_frame_height = base_height * min_ratio

        # Set scale_factor for card size.
        self.scale_factor: float = scale_factor_multiplier * window_size_factor

        # Determine window rectangle.
        window_width: int = int(max_frame_width * window_size_factor)
        window_height: int = int(max_frame_height * window_size_factor)
        window_x: int = int((working_screen_width - window_width) / 2) + 300
        window_y: int = int((working_screen_height - window_height) / 2)
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

        # Create canvas.
        self.game_canvas = GameCanvas(parent=self, window_width=window_width,
                                      window_height=window_height,
                                      scale_factor=self.scale_factor,
                                      gin_rummy_env=gin_rummy_env)
        self.pack()  # FIXME: I don't understand how pack, grid, place work

        if is_debug:
            self.update()
            print(f"screen size is {screenwidth}x{screenheight}")
            print(f"working screen size is {working_screen_width}x{working_screen_height}")
            print(f"(base_width, base_height) is ({base_width}, {base_height})")
            print(f"(window_width, window_height) is ({window_width}, {window_height})")
            print(f"window size is ({self.winfo_width()}, {self.winfo_height()})")
            print(f"window_size_factor={window_size_factor}")
            print(f"scale_factor={self.scale_factor}")

    def get_dealer_id(self) -> int:
        return self.game_canvas.dealer_id

    def start_new_game(self):
        starting_new_game.start_new_game(game_canvas=self.game_canvas)

    def update_configurations(self):
        self.game_canvas.update_configurations()

    def update_configuration_game_background_color(self, color):
        self.game_canvas.configure(background=color)
