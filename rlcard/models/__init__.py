''' Register rule-based models or pre-trianed models
'''

from rlcard.models.registration import register, load

register(
    model_id = 'leduc-holdem-nfsp',
    entry_point='rlcard.models.pretrained_models:LeducHoldemNFSPModel')
