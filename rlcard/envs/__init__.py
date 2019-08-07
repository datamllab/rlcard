from rlcard.envs.regiteration import register, make

### Example... This one does work for now 

register(
    id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)