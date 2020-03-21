import unittest

from rlcard.agents.uno_human_agent import _print_state, _print_action

class TestLeducHuman(unittest.TestCase):

    def test_print_state(self):
        raw_state = {'target': 'r-reverse', 'current_player': 0, 'legal_actions': ['r-2', 'r-draw_2'], 'hand': ['y-skip', 'y-draw_2', 'r-2', 'b-3', 'b-6', 'g-wild_draw_4', 'r-draw_2'], 'played_cards': ['g-reverse', 'r-reverse'], 'player_num': 2, 'others_hand': ['y-4', 'g-6', 'b-reverse', 'b-5', 'b-reverse', 'r-9'], 'card_num': [7, 6]}
        action_record = []
        _print_state(raw_state, action_record)

    def test_print_action(self):
        _print_action('r-8')
