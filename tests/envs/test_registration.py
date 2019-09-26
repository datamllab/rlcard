import unittest

import rlcard
from rlcard.envs.registration import *


class TestRegistration(unittest.TestCase):

    def test_register(self):
        register(env_id='test_reg', entry_point='rlcard.envs.blackjack:BlackjackEnv')
        with self.assertRaises(ValueError):
            register(env_id='test_reg', entry_point='rlcard.envs.blackjack:BlackjackEnv')

    def test_make(self):
        register(env_id='test_make', entry_point='rlcard.envs.blackjack:BlackjackEnv')
        env = rlcard.make('test_make')
        _, player = env.init_game()
        self.assertEqual(player, 0)
        with self.assertRaises(ValueError):
            make('test_random_make')

if __name__ == '__main__':
    unittest.main()
