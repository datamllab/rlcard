''' Register new environments
'''

from rlcard.envs.registration import register, make


register(
    id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)

register(
    id='blackjack',
    entry_point='rlcard.envs.blackjack:BlackjackEnv',
)

#register(
#    id='simpletexasholdem',
#    entry_point='rlcard.envs.simpletexasholdem:SimpleTexasEnv',
#)

#register(
#    id='texasholdem',
#    entry_point='rlcard.envs.texasholdem:TexasEnv',
#)
