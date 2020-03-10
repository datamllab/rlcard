#
#   Gin Rummy
#

from configparser import ConfigParser

#
#   Chess parameters from the Chess program by Bhaskar Chaudhary
#

X_AXIS_LABELS = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H')
Y_AXIS_LABELS = (1, 2, 3, 4, 5, 6, 7, 8)

START_PIECES_POSITION = {
    "A8": "r", "B8": "n", "C8": "b", "D8": "q", "E8": "k", "F8": "b", "G8": "n", "H8": "r",
    "A7": "p", "B7": "p", "C7": "p", "D7": "p", "E7": "p", "F7": "p", "G7": "p", "H7": "p",
    "A2": "P", "B2": "P", "C2": "P", "D2": "P", "E2": "P", "F2": "P", "G2": "P", "H2": "P",
    "A1": "R", "B1": "N", "C1": "B", "D1": "Q", "E1": "K", "F1": "B", "G1": "N", "H1": "R"
}

SHORT_NAME = {'R': 'Rook',  'N': 'Knight',  'B': 'Bishop',  'Q': 'Queen', 'K': 'King',  'P': 'Pawn'}

ORTHOGONAL_POSITIONS = ((-1, 0), (0, 1), (1, 0), (0, -1))
DIAGONAL_POSITIONS = ((-1, -1), (-1, 1), (1, -1), (1, 1))
KNIGHT_POSITIONS = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))

#
#   Gin Rummy parameters
#

GOING_OUT_DEADWOOD_COUNT = 10

#
#   RLCard Gin Rummy parameters
#

MAX_DRAWN_CARD_COUNT = 52 - 46

DISCARD_PILE_TAG = "discard_pile"
STOCK_PILE_TAG = "stock_pile"
NORTH_HELD_PILE_TAG = "north_held_pile"
SOUTH_HELD_PILE_TAG = "south_held_pile"
PLAYER_HELD_PILE_TAGS = [NORTH_HELD_PILE_TAG, SOUTH_HELD_PILE_TAG]

DRAWN_TAG = "drawn"
JOGGED_TAG = "jogged"
SELECTED_TAG = "selected"

# DRAW_FROM_STOCK_PILE_TYPE = 0
# DRAW_FROM_DISCARD_PILE_TYPE = 1
# DECLARE_DEAD_HAND_TYPE = 2
# DISCARD_TYPE = 3
# KNOCK_TYPE = 55

SCORE_PLAYER_0_ACTION_ID = 0
SCORE_PLAYER_1_ACTION_ID = 1
DRAW_CARD_ACTION_ID = 2
PICK_UP_DISCARD_ACTION_ID = 3
DECLARE_DEAD_HAND_ACTION_ID = 4
GIN_ACTION_ID = 5
DISCARD_ACTION_ID = 6
KNOCK_ACTION_ID = DISCARD_ACTION_ID + 52

#
#   User Modifiable Options
#

config = ConfigParser()
config.read('game_options.ini')

# settings section
settings_section = "settings"
show_status_messages_option = "show_status_messages"
warning_as_option = 'warning_as'
game_background_color_option = 'game_background_color'
window_size_factor_option = 'window_size_factor'

SHOW_STATUS_MESSAGES = config.get(section=settings_section, option=show_status_messages_option, fallback="verbose")
WARNINGS_AS = config.get(section=settings_section, option=warning_as_option, fallback="alert_messages")
GAME_BACKGROUND_COLOR = config.get(section=settings_section, option=game_background_color_option, fallback="#007F00")
WINDOW_SIZE_FACTOR = config.get(section=settings_section, option=window_size_factor_option, fallback="75")
