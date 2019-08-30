from rlcard.envs.regiteration import register, make

### Example... This one does work for now 
register(
    id='blackjack',
    entry_point='rlcard.envs.blackjack:BlackjackEnv',
)

register(
    id='doudizhu',
    entry_point='rlcard.envs.doudizhu:DoudizhuEnv',
)

<<<<<<< HEAD
=======
register(
    id='simpletexasholdem',
    entry_point='rlcard.envs.simpletexasholdem:SimpleTexasEnv',
)
>>>>>>> 94702c8651ab41508d76cd5b62e2ea6d5dc83deb
