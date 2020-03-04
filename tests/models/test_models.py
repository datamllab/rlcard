import unittest

from rlcard.models.model import Model
from rlcard.models.pretrained_models import LeducHoldemNFSPModel, LeducHoldemCFRModel
from rlcard.models.leducholdem_rule_models import LeducHoldemRuleModelV1, LeducHoldemRuleModelV2

class TestModel(unittest.TestCase):

    def test_model(self):
        model = Model()
        self.assertIsInstance(model, Model)

    def test_leduc_holdem_nfsp_model(self):
        model = LeducHoldemNFSPModel()
        self.assertIsInstance(model, LeducHoldemNFSPModel)
        self.assertIsInstance(model.agents, list)
        
    def test_leduc_holdem_cfr_model(self):
        model = LeducHoldemCFRModel()
        self.assertIsInstance(model, LeducHoldemCFRModel)
        self.assertIsInstance(model.agents, list)

    def test_leduc_holdem_rule_model_v1(self):
        model = LeducHoldemRuleModelV1()
        self.assertIsInstance(model, LeducHoldemRuleModelV1)
        agent = model.agents[0]
        action = agent.step({'raw_legal_actions':['raise']})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['call']})
        self.assertEqual(action, 'call')
        action = agent.step({'raw_legal_actions':['check']})
        self.assertEqual(action, 'check')
        action = agent.step({'raw_legal_actions':[]})
        self.assertEqual(action, 'fold')

    def test_leduc_holdem_rule_model_v2(self):
        model = LeducHoldemRuleModelV2()
        self.assertIsInstance(model, LeducHoldemRuleModelV2)
        # TODO: Add detailed tests

if __name__ == '__main__':
    unittest.main()
