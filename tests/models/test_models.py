import unittest

from rlcard.models.model import Model
from rlcard.models.pretrained_models import LeducHoldemNFSPModel, LeducHoldemNFSPPytorchModel, LeducHoldemCFRModel
from rlcard.models.leducholdem_rule_models import LeducHoldemRuleModelV1, LeducHoldemRuleModelV2

from rlcard.models.limitholdem_rule_models import LimitholdemRuleModelV1
from rlcard.models.doudizhu_rule_models import DouDizhuRuleModelV1
class TestModel(unittest.TestCase):

    def test_model(self):
        model = Model()
        self.assertIsInstance(model, Model)

    def test_leduc_holdem_nfsp_model(self):
        model = LeducHoldemNFSPModel()
        self.assertIsInstance(model, LeducHoldemNFSPModel)
        self.assertIsInstance(model.agents, list)

    def test_leduc_holdem_nfsp_pytorch_model(self):
        model = LeducHoldemNFSPPytorchModel()
        self.assertIsInstance(model, LeducHoldemNFSPPytorchModel)
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
        agent = model.agents[0]
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['K'], 'public_card':[]}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['Q'], 'public_card':[]}})
        self.assertEqual(action, 'check')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['J'], 'public_card':[]}})
        self.assertEqual(action, 'fold')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['K', 'J'], 'public_card':['K','J']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['K', 'Q'], 'public_card':['K','J']}})
        self.assertEqual(action, 'fold')
        action = agent.step({'raw_legal_actions':['fold', 'check', 'call'], 'raw_obs':{'hand':['K'], 'public_card':[]}})
        self.assertEqual(action, 'call')
        action = agent.step({'raw_legal_actions':['fold', 'call'], 'raw_obs':{'hand':['Q'], 'public_card':[]}})
        self.assertEqual(action, 'fold')

    def test_limit_holdem_rule_model_v1(self):
        model = LimitholdemRuleModelV1()
        self.assertIsInstance(model, LimitholdemRuleModelV1)
        agent = model.agents[0]
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['S2', 'H4'], 'public_cards':[]}})
        self.assertEqual(action, 'fold')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HA'], 'public_cards':[]}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HT'], 'public_cards':[]}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['S2', 'SA'], 'public_cards':[]}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['HQ', 'SJ'], 'public_cards':[]}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['HQ', 'S2'], 'public_cards':[]}})
        self.assertEqual(action, 'fold')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HA'], 'public_cards':['CA', 'C2', 'B4']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HQ'], 'public_cards':['CJ', 'C2', 'B4']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['HA', 'H9'], 'public_cards':['HJ', 'C2', 'B4']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SK', 'HQ'], 'public_cards':['H6', 'C2', 'B4']}})
        self.assertEqual(action, 'call')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SK', 'HQ'], 'public_cards':['H2', 'C2', 'B4']}})
        self.assertEqual(action, 'check')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HA'], 'public_cards':['CA', 'C2', 'B4', 'B6']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SA', 'HQ'], 'public_cards':['CJ', 'C2', 'B4', 'B6']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['H9', 'HA'], 'public_cards':['HJ', 'C2', 'B4', 'B6']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['H9', 'HA'], 'public_cards':['HJ', 'C2', 'B4', 'B6']}})
        self.assertEqual(action, 'raise')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SK', 'HQ'], 'public_cards':['H6', 'C2', 'B4', 'B5']}})
        self.assertEqual(action, 'call')
        action = agent.step({'raw_legal_actions':['raise', 'fold', 'check', 'call'], 'raw_obs':{'hand':['SK', 'HQ'], 'public_cards':['H2', 'C2', 'B4', 'B5']}})
        self.assertEqual(action, 'fold')

    def test_doudizhu_rule_model_v1(self):
        model = DouDizhuRuleModelV1()
        self.assertIsInstance(model, DouDizhuRuleModelV1)
        agent = model.agents[0]
        action = agent.step({'raw_obs': {'current_hand': '345567999TTTTQKAA2BR', 'trace':[]}})
        self.assertEqual(action, '34567')
        action = agent.step({'raw_obs': {'current_hand': '5999TTTTQKAA2BR', 'trace':[(0, '34567'), (1, 'pass'), (2, 'pass')]}})
        self.assertEqual(action, '5')
        action = agent.step({'raw_obs': {'actions': ['pass', '44455', '44466', 'TTTT', 'BR'], 'trace':[(0, '33344')]}})
        self.assertEqual(action, '44455')
        action = agent.step({'raw_obs': {'actions': ['pass', '44455', '44466', 'TTTT', 'BR'], 'trace':[(0, '33344'), [1, 'pass']]}})
        self.assertEqual(action, '44455')
        action = agent.step({'raw_obs': {'actions': ['pass', 'TTTT', 'BR'], 'self': 2, 'landlord': 0, 'trace':[(0, '33344'), (1, '55566')]}})
        self.assertEqual(action, 'pass')

if __name__ == '__main__':
    unittest.main()
