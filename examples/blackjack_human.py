''' A toy example of self playing for Blackjack
    Multiple agent game implemented (except dqn agent)
'''

import rlcard
from rlcard.agents import RandomAgent as RandomAgent
from rlcard.agents import BlackjackHumanAgent as HumanAgent

from rlcard.utils.utils import print_card

# Make environment and enable human mode
# Set 'record_action' to True because we need it to print results
env = rlcard.make('blackjack', config={'record_action': True})
human_agent = HumanAgent(env.action_num)
random_agent = RandomAgent(env.action_num)
env.set_agents([human_agent, random_agent])
num_players = 2

"""
multi agents is available without dqn agent
dqn agent now runs in single agent environment only
so someone need to change codes for multi dqn agent play
"""

print(">> Blackjack human and random agent")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action

    final_state = []
    action_record = []
    state = []
    _action_list = []

    if len(trajectories[0]) != 0:
        for i in range(num_players):
            final_state.append(trajectories[i][-1][-2])
            action_record.append(final_state[i]['action_record'])
            state.append(final_state[i]['raw_obs'])
            _action_list.append([])
            for j in range(1, len(action_record)+1):
                _action_list.insert(0, action_record[-j])

        for pair in _action_list[i]:
            print('>> Player', pair[0], 'chooses', pair[1])

    # Let's take a look at what the agent card is
    print('===============   Dealer hand   ===============')
    print_card(state[0]['state'][1])

    for i in range(num_players):
        print('===============   Player {} Hand   ==============='.format(i))
        print_card(state[i]['state'][0])

    print('===============     Result     ===============')
    for i in range(num_players):
        if payoffs[i] == 1:
            print('Player {} win {} chip!'.format(i, payoffs[i]))
        elif payoffs[i] == 0:
            print('Player {} is tie'.format(i))
        else:
            print('Player {} lose {} chip!'.format(i, -payoffs[i]))
        print('')

    input("Press any key to continue...")
