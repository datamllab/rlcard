''' Register new environments
'''

from rlcard.envs.registration import register, make

register(
    env_id='blackjack',
    entry_point='rlcard.envs.blackjack:BlackjackEnv',
)

register(
    env_id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)

register(
    env_id='limit-holdem',
    entry_point='rlcard.envs.limitholdem:LimitholdemEnv',
)

register(
    env_id='no-limit-holdem',
    entry_point='rlcard.envs.nolimitholdem:NolimitholdemEnv',
)

register(
    env_id='uno',
    entry_point='rlcard.envs.uno:UnoEnv',
)
