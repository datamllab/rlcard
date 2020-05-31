''' A toy example of self playing for Blackjack
    Maybe it is used to play against multiple trained agents if someone can rebuild a game code :)
'''

import rlcard
from rlcard.agents import BlackjackHumanAgent as HumanAgent
from rlcard.utils.utils import print_card

# Make environment and enable human mode
# Set 'record_action' to True because we need it to print results
env = rlcard.make('blackjack', config={'record_action': True})
human_agent = HumanAgent(env.action_num)
env.set_agents([human_agent])

print(">> Blackjack human agent")

while (True):
    print(">> Start a new game")

    trajectories, payoffs = env.run(is_training=False)
    # If the human does not take the final action, we need to
    # print other players action
    if len(trajectories[0]) != 0:
        final_state = trajectories[0][-1][-2]
        action_record = final_state['action_record']
        state = final_state['raw_obs']
        _action_list = []
        for i in range(1, len(action_record)+1):
            _action_list.insert(0, action_record[-i])
        for pair in _action_list:
            print('>> Player', pair[0], 'chooses', pair[1])

    # Let's take a look at what the agent card is
    print('===============   Dealer hand   ===============')
    print_card(state['state'][1])
    print('===============    Your Hand    ===============')
    print_card(state['state'][0])

    print('===============     Result     ===============')
    if payoffs[0] > 0:
        print('You win {} chips!'.format(payoffs[0]))
    elif payoffs[0] == 0:
        print('It is a tie.')
    else:
        print('You lose {} chips!'.format(-payoffs[0]))
    print('')

    input("Press any key to continue...")
