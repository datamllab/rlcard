from rlcards.envs.registration import register, make

### Example... This one does work for now 

register(
    id='doudizhu',
    entry_point='rlcards.envs.doudizhu.DoudizhuEnv',
)