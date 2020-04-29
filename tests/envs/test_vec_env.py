import unittest
import numpy as np

import rlcard
from rlcard.agents import RandomAgent
from .determism_util import is_deterministic

class TestVecEnv(unittest.TestCase):

    def test_vec_env(self):
        env = rlcard.make('limit-holdem', config={'env_num': 4})
        env.set_agents([RandomAgent(env.action_num) for _ in range(env.player_num)])
        trajectories, payoffs = env.run(is_training=False)
        self.assertEqual(len(payoffs), 4)
        trajectories, payoffs = env.run(is_training=True)

if __name__ == '__main__':
    unittest.main()
