import unittest
import numpy as np

from rlcard.models.model import Model
from rlcard.models.pretrained_models import LeducHoldemNFSPModel

class TestModel(unittest.TestCase):

    def test_model(self):
        model = Model()

    def test_leduc_holdem_nfsp_model(self):
        model = LeducHoldemNFSPModel()

if __name__ == '__main__':
    unittest.main()
