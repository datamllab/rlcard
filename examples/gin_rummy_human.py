#
#   Gin Rummy
#

import tkinter as tk

import rlcard

from rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.menu_bar import MenuBar
from rlcard.agents.gin_rummy_human_agent.gui_gin_rummy.game_frame import GameFrame

# Make environment and enable human mode
gin_rummy_env = rlcard.make('gin-rummy')

# Play game
root = tk.Tk()
root.resizable(False, False)
game_frame = GameFrame(root=root, gin_rummy_env=gin_rummy_env)
menu_bar = MenuBar(root, game_frame=game_frame)
game_frame.start_new_game()
root.mainloop()
