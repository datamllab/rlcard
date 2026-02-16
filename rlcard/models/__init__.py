''' Register rule-based models or pre-trianed models
'''
from rlcard.models.registration import register, load

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

register(
    model_id = 'limit-holdem-rule-v1',
    entry_point='rlcard.models.limitholdem_rule_models:LimitholdemRuleModelV1')

register(
    model_id = 'doudizhu-rule-v1',
    entry_point='rlcard.models.doudizhu_rule_models:DouDizhuRuleModelV1')

register(
    model_id='gin-rummy-novice-rule',
    entry_point='rlcard.models.gin_rummy_rule_models:GinRummyNoviceRuleModel')

register(
    model_id='bauernskat-rule-random',
    entry_point='rlcard.models.bauernskat_rule_models:BauernskatRandomRuleModelV1')

register(
    model_id='bauernskat-rule-frugal',
    entry_point='rlcard.models.bauernskat_rule_models:BauernskatFrugalRuleModelV1')

register(
    model_id='bauernskat-rule-lookahead',
    entry_point='rlcard.models.bauernskat_rule_models:BauernskatLookaheadRuleModelV1')

register(
    model_id='bauernskat-rule-shot-alphabeta',
    entry_point='rlcard.models.bauernskat_rule_models:BauernskatSHOTAlphaBetaRuleModelV1')