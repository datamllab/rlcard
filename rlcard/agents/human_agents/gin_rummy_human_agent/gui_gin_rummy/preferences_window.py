'''
    Project: Gui Gin Rummy
    File name: preferences_window.py
    Author: William Hale
    Date created: 3/14/2020
'''

from tkinter import *
import tkinter.colorchooser as colorchooser
from configparser import ConfigParser

from . import configurations
from .configurations import config_path
from .configurations import settings_section
from .configurations import show_status_messages_option, warning_as_option, game_background_color_option
from .configurations import window_size_factor_option
from .configurations import is_show_tips_option
from .configurations import is_debug_option


class PreferencesWindow(object):

    #
    # The game_background_color is updated immediately when returned from color dialog.
    # If the preference dialog is cancelled, the original game_background_color is restored.
    #

    # Note:
    #   The file game_options.ini must already exists with the settings sections existing at least.
    #   For this program, the line "[settings]" is the minimal that is required.

    def __init__(self, view):
        self.parent = view.master
        self.view = view

        # create preferences window
        self.pref_window = Toplevel(self.parent)
        self.pref_window.title("Gin Rummy Preferences")

        # fill preferences that cannot be obtained from their widgets
        self.game_background_color = configurations.GAME_BACKGROUND_COLOR
        self.original_game_background_color = self.game_background_color  # used if color dialog cancelled

        # create preferences pane (can be rearranged within same section)
        row = 0

        # Preference: Show status messages
        row += 1
        self.show_status_messages_listbox = self.create_choice_line(row=row, choice_name=show_status_messages_option)

        # Preference: Warnings as
        row += 1
        self.warnings_as_listbox = self.create_choice_line(row=row, choice_name=warning_as_option)

        # Preference: Game background color
        row += 1
        Label(self.pref_window, text="Game background color").grid(row=row, sticky=W, padx=5, pady=5)
        self.game_background_color_button = Button(self.pref_window, text='Select color')
        self.game_background_color_button.configure(command=self.set_game_background_color)
        self.game_background_color_button.grid(row=row, column=1, columnspan=2, sticky=W, padx=5, pady=5)

        # Preference: Window size
        row += 1
        Label(self.pref_window, text="Window size (percent)").grid(row=row, sticky=W, padx=5, pady=5)
        self.window_size_scale = Scale(self.pref_window, from_=50, to=100, orient=HORIZONTAL)
        self.window_size_scale.set(configurations.WINDOW_SIZE_FACTOR)
        self.window_size_scale.grid(row=row, column=1, columnspan=2, sticky=W, padx=5, pady=5)

        # Preference: is_show_tips
        row += 1
        self.is_show_tips = BooleanVar()
        self.is_show_tips.set(configurations.IS_SHOW_TIPS)
        self.is_show_tips_checkbutton = self.create_checkbutton(text="show tips", variable=self.is_show_tips)
        self.is_show_tips_checkbutton.grid(row=row, column=0, columnspan=3, sticky=W, padx=5, pady=5)

        # Preference: is_debug
        row += 1
        self.is_debug = BooleanVar()
        self.is_debug.set(configurations.IS_DEBUG)
        self.is_debug_checkbutton = self.create_checkbutton(text="is debug", variable=self.is_debug)
        self.is_debug_checkbutton.grid(row=row, column=0, columnspan=3, sticky=W, padx=5, pady=5)

        # create cancel and save buttons
        row += 1
        cancel_button = Button(self.pref_window, text="Cancel", command=self.on_cancel_button_clicked)
        cancel_button.grid(row=row, column=1, sticky=E, padx=5, pady=5)
        save_button = Button(self.pref_window, text="Save", command=self.on_save_button_clicked)
        save_button.grid(row=row, column=2, sticky=E, padx=5, pady=5)

        # wrap up
        self.pref_window.transient(self.parent)

    def set_game_background_color(self):  # store because color cannot be obtained from its widget
        self.game_background_color = colorchooser.askcolor(initialcolor=self.game_background_color)[-1]
        self.view.update_configuration_game_background_color(background_color=self.game_background_color)

    def on_save_button_clicked(self):
        self.set_new_values()
        self.pref_window.destroy()
        self.view.update_configurations()

    def set_new_values(self):
        config = ConfigParser()
        config.read(config_path)

        show_status_messages = self.show_status_messages_listbox.get(ACTIVE)
        configurations.SHOW_STATUS_MESSAGES = show_status_messages
        config.set(settings_section, show_status_messages_option, show_status_messages)

        warnings_as = self.warnings_as_listbox.get(ACTIVE)
        configurations.WARNINGS_AS = warnings_as
        config.set(settings_section, warning_as_option, warnings_as)

        configurations.GAME_BACKGROUND_COLOR = self.game_background_color
        config.set(settings_section, game_background_color_option, self.game_background_color)

        window_size_factor = self.window_size_scale.get()
        configurations.WINDOW_SIZE_FACTOR = window_size_factor
        config.set(settings_section, window_size_factor_option, str(window_size_factor))  # Note: using str

        is_show_tips = self.is_show_tips.get()
        configurations.IS_SHOW_TIPS = is_show_tips
        config.set(settings_section, is_show_tips_option, str(is_show_tips))  # Note: using str

        is_debug = self.is_debug.get()
        configurations.IS_DEBUG = is_debug
        config.set(settings_section, is_debug_option, str(is_debug))  # Note: using str

        with open(config_path, 'w') as config_file:
            config.write(config_file)

    def on_cancel_button_clicked(self):
        self.view.update_configuration_game_background_color(background_color=self.original_game_background_color)
        self.pref_window.destroy()

    def create_checkbutton(self, text: str, variable: BooleanVar):
        checkbutton = Checkbutton(self.pref_window, text=text, variable=variable)
        return checkbutton

    def create_listbox(self, row, column, columnspan, items):
        listbox = Listbox(self.pref_window, height=0, width=0)
        listbox.configure(exportselection=0)  # note this
        for item in items:
            listbox.insert(END, item)
        listbox.grid(row=row, column=column, columnspan=columnspan, sticky=W, padx=5, pady=5)
        return listbox

    def create_choice_line(self, row: int, choice_name: str):
        listbox = None
        items = None
        selected_item = None
        if choice_name == show_status_messages_option:
            Label(self.pref_window, text="Show status messages").grid(row=row, sticky=W, padx=5, pady=5)
            items = ["verbose", "brief", 'none']
            selected_item = configurations.SHOW_STATUS_MESSAGES
        elif choice_name == warning_as_option:
            Label(self.pref_window, text="Warnings as").grid(row=row, sticky=W, padx=5, pady=5)
            items = ["alert messages", "beeps"]
            selected_item = configurations.WARNINGS_AS
        if items is not None:
            listbox = self.create_listbox(row=row, column=1, columnspan=2, items=items)
            selected_item_index = 0
            if selected_item in items:
                selected_item_index = items.index(selected_item)
            listbox.selection_set(first=selected_item_index)
            listbox.activate(index=selected_item_index)
        return listbox
