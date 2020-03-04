''' Register rule-based models or pre-trianed models
'''

from rlcard.models.registration import register, load

try:
    register(
        model_id = 'leduc-holdem-nfsp',
        entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')
except:
    pass

register(
    model_id = 'leduc-holdem-cfr',
    entry_point='rlcard.models.pretrained_models:LeducHoldemCFRModel')

register(
    model_id = 'leduc-holdem-rule-v1',
    entry_point='rlcard.models.leducholdem_rule_models:LeducHoldemRuleModelV1')

register(
    model_id = 'leduc-holdem-rule-v2',
    entry_point='rlcard.models.leducholdem_rule_models:LeducHoldemRuleModelV2')

register(
    model_id = 'uno-rule-v1',
    entry_point='rlcard.models.uno_rule_models:UNORuleModelV1')
