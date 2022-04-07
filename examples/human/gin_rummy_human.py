'''
    Project: Gui Gin Rummy
    File name: gin_rummy_human.py
    Author: William Hale
    Date created: 3/14/2020
'''

#   You need to install tkinter if it is not already installed.
#   Tkinter is Python's defacto standard GUI (Graphical User Interface) package.
#   It is a thin object-oriented layer on top of Tcl/Tk.
#   Note that the name of the module is ‘tkinter’.
#
#   If you are using anaconda:
#       -- I have version 8.6.11 to work with version 3.6 of Python.
#       -- In the installed window for your environment, search for "tk".
#       -- If it is found, make sure you have at least version 8.6.11.
#       -- Otherwise, go to the "Not installed" window, search for "tk", select it, and apply it.
#
#   If you are using Ubuntu:
#       -- You can install it with apt-get install python-tk.
#
#   For other cases, you can search on google to see how to install tkinter.

# from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from rlcard.envs.gin_rummy import GinRummyEnv

import rlcard

from rlcard.agents import RandomAgent
from rlcard.models.gin_rummy_rule_models import GinRummyNoviceRuleAgent
from rlcard.agents.human_agents.gin_rummy_human_agent.gin_rummy_human_agent import HumanAgent

from rlcard.agents.human_agents.gin_rummy_human_agent.gui_gin_rummy.game_app import GameApp

from rlcard.games.gin_rummy.utils import scorers


def make_gin_rummy_env() -> 'GinRummyEnv':
    gin_rummy_env = rlcard.make('gin-rummy')
    # north_agent = RandomAgent(num_actions=gin_rummy_env.num_actions)
    north_agent = GinRummyNoviceRuleAgent()
    south_agent = HumanAgent(gin_rummy_env.num_actions)
    gin_rummy_env.set_agents([
        north_agent,
        south_agent
    ])
    gin_rummy_env.game.judge.scorer = scorers.GinRummyScorer(get_payoff=scorers.get_payoff_gin_rummy_v0)
    return gin_rummy_env


# Play game
gin_rummy_app = GameApp(make_gin_rummy_env=make_gin_rummy_env)
