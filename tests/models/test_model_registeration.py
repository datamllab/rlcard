import unittest

from  rlcard import models
from rlcard.models.registration import register, load


class TestRegistration(unittest.TestCase):

    def test_register(self):
        register(model_id='test_reg', entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')
        with self.assertRaises(ValueError):
            register(model_id='test_reg', entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')

    def test_load(self):
        register(model_id='test_load', entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')
        models.load('test_load')
        with self.assertRaises(ValueError):
            load('test_random_make')

if __name__ == '__main__':
    unittest.main()
