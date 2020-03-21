import unittest

from rlcard.agents.leduc_holdem_human_agent import _print_state

class TestLeducHuman(unittest.TestCase):

    def test_print_state(self):
        raw_state = {'my_chips': 1, 'current_player': 0, 'all_chips': [1, 1], 'public_card': None, 'hand': 'SQ', 'legal_actions': ['raise', 'fold', 'check']}
        action_record = []
        _print_state(raw_state, action_record)

