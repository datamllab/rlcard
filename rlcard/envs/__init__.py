from rlcard.envs.regiteration import register, make

### Example... This one does work for now 

register(
    id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)

register(
    id='simpletexasholdem',
    entry_point='rlcard.envs.simpletexasholdem:SimpleTexasEnv',
)