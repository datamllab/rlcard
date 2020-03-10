''' A toy example of playing against rule-based bot on UNO
'''

import rlcard
from rlcard import models
from rlcard.agents.uno_human_agent import HumanAgent

# Make environment and enable human mode
# Set 'record_action' to True because we need it to print results
env = rlcard.make('uno', config={'record_action': True})
human_agent = HumanAgent(env.action_num)
cfr_agent = models.load('uno-rule-v1').agents[0]
env.set_agents([human_agent, cfr_agent])

print(">> UNO rule model V1")

while (True):
    print(">> Start a new game")

    _, payoffs = env.run(is_training=False)
    print('===============     Result     ===============')
    if payoffs[0] > 0:
        print('You win!')
    else:
        print('You lose!')
    print('')
    input("Press any key to continue...")
