''' A toy example of playing against rule-based bot on UNO
'''

import rlcard
from rlcard import models
from rlcard.agents.uno_human_agent import HumanAgent, _print_action

# Make environment and enable human mode
# Set 'record_action' to True because we need it to print results
env = rlcard.make('uno', config={'record_action': True})
human_agent = HumanAgent(env.action_num)
cfr_agent = models.load('uno-rule-v1').agents[0]
env.set_agents([human_agent, cfr_agent])

print(">> UNO rule model V1")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    final_state = trajectories[0][-1][-2]
    action_record = final_state['action_record']
    state = final_state['raw_obs']
    _action_list = []
    for i in range(1, len(action_record)+1):
        if action_record[-i][0] == state['current_player']:
            break
        _action_list.insert(0, action_record[-i])
    for pair in _action_list:
        print('>> Player', pair[0], 'chooses ', end='')
        _print_action(pair[1])
        print('')

    print('===============     Result     ===============')
    if payoffs[0] > 0:
        print('You win!')
    else:
        print('You lose!')
    print('')
    input("Press any key to continue...")
