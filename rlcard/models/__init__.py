''' Register rule-based models or pre-trianed models
'''

from rlcard.models.registration import register, load

register(
    model_id = 'leduc-holdem-nfsp',
    entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')

register(
    model_id = 'uno-rule-v1',
    entry_point='rlcard.models.uno_rule_models:UNORuleModelV1')
