'''
    File name: rlcard/games/bauernskat/config.py
    Author: Oliver Czerwinski
    Date created: 07/17/2025
    Date last modified: 12/25/2025
'''

# Deck Configuration

# Defines suits and ranks
VALID_SUITS: tuple[str, ...] = ('C', 'S', 'H', 'D')
VALID_RANKS: tuple[str, ...] = ('7', '8', '9', 'Q', 'K', '10', 'A', 'J')

# Defines pip value of each rank
RANK_VALUES: dict[str, int] = {
    '7': 0, '8': 0, '9': 0, 'Q': 3, 'K': 4, '10': 10, 'A': 11, 'J': 2
}


# Player and Layout Configuration

NUM_PLAYERS: int = 2
NUM_COLUMNS_PER_PLAYER: int = 8


# Action Space Configuration

GRAND_AVAILABLE: bool = True

# Trump actions (4 suits + 1 grand)
NUM_DECLARE_TRUMP_ACTIONS: int = len(VALID_SUITS) + (int(GRAND_AVAILABLE) * 1)

FIRST_DECLARE_TRUMP_ACTION_ID: int = 0
FIRST_PLAY_CARD_ACTION_ID: int = FIRST_DECLARE_TRUMP_ACTION_ID + NUM_DECLARE_TRUMP_ACTIONS

NUM_CARDS_IN_DECK: int = len(VALID_SUITS) * len(VALID_RANKS)
TOTAL_NUM_ACTIONS: int = NUM_DECLARE_TRUMP_ACTIONS + NUM_CARDS_IN_DECK


# History Construction Configuration

HISTORY_SEQUENCE_LENGTH: int = 33
HISTORY_FRAME_SIZE: int = 49