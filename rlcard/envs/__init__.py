''' Register new environments
'''

from rlcard.envs.registration import register, make

register(
    id='blackjack',
    entry_point='rlcard.envs.blackjack:BlackjackEnv',
)

register(
    id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)

register(
    id='limit-holdem',
    entry_point='rlcard.envs.limitholdem:LimitholdemEnv',
)
