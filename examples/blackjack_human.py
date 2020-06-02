''' A toy example of self playing for Blackjack
    Maybe it is used to play against multiple trained agents if someone can rebuild a game code :)
'''

import rlcard
from rlcard.agents import RandomAgent as RandomAgent
from rlcard.agents import BlackjackHumanAgent as HumanAgent
from rlcard.utils.utils import print_card

# Make environment and enable human mode
# Set 'record_action' to True because we need it to print results
player_num = 2
env = rlcard.make('blackjack', config={'record_action': True, 'game_player_num': player_num})
human_agent = HumanAgent(env.action_num)
random_agent = RandomAgent(env.action_num)
env.set_agents([human_agent, random_agent])

print(">> Blackjack human agent")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action

    if len(trajectories[0]) != 0:
        final_state = []
        action_record = []
        state = []
        _action_list = []

        for i in range(player_num):
            final_state.append(trajectories[i][-1][-2])
            state.append(final_state[i]['raw_obs'])

        action_record.append(final_state[i]['action_record'])
        for i in range(1, len(action_record) + 1):
            _action_list.insert(0, action_record[-i])

        for pair in _action_list[0]:
            print('>> Player', pair[0], 'chooses', pair[1])

    # Let's take a look at what the agent card is
    print('===============   Dealer hand   ===============')
    print_card(state[0]['state'][1])

    for i in range(player_num):
        print('===============   Player {} Hand   ==============='.format(i))
        print_card(state[i]['state'][0])

    print('===============     Result     ===============')
    for i in range(player_num):
        if payoffs[i] == 1:
            print('Player {} win {} chip!'.format(i, payoffs[i]))
        elif payoffs[i] == 0:
            print('Player {} is tie'.format(i))
        else:
            print('Player {} lose {} chip!'.format(i, -payoffs[i]))
        print('')

    input("Press any key to continue...")
