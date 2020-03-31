'''
    Project: Gui Gin Rummy
    File name: menu_bar.py
    Author: William Hale
    Date created: 3/14/2020
'''

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .game_frame import GameFrame

import tkinter as tk
from tkinter import messagebox

from .preferences_window import PreferencesWindow


class MenuBar(tk.Menu):

    def __init__(self, root: tk.Tk, game_frame: 'GameFrame'):
        super().__init__(root)
        self.game_frame = game_frame

        # create file menu
        file_menu = tk.Menu(self, tearoff=False)
        file_menu.add_command(label="New Game", command=self.on_new_game_menu_clicked)
        self.add_cascade(label="File", menu=file_menu)

        # create edit menu
        edit_menu = tk.Menu(self, tearoff=False)
        edit_menu.add_command(label="Preferences", command=self.on_preference_menu_clicked)
        self.add_cascade(label="Edit", menu=edit_menu)

        # create about menu
        help_menu = tk.Menu(self, tearoff=False)
        help_menu.add_command(label="About", command=self.on_about_menu_clicked)
        self.add_cascade(label="Help", menu=help_menu)

        # configure menuBar
        root.configure(menu=self)

    def on_new_game_menu_clicked(self):
        self.game_frame.start_new_game()

    def on_preference_menu_clicked(self):
        PreferencesWindow(self.game_frame)

    @staticmethod
    def on_about_menu_clicked():
        messagebox.showinfo(title="Info", message="Gin Rummy\nVersion 1.0")
