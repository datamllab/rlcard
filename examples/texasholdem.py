# Example of using doudizhu environment
import rlcard
from rlcard.agents.random_agent import RandomAgent

# make environment
env = rlcard.make('texasholdem')

print('############## Environment of Texas Holdem Initilized ################')

env.test()

# set agents
agent_0 = RandomAgent()
agent_1 = RandomAgent()
env.set_agents([agent_0, agent_1])

# seed everything
env.set_seed(0)
agent_0.set_seed(0)
agent_1.set_seed(0)

for _ in range(1):
    # generate data from the environment
    trajectories, player_wins = env.run()
    print(trajectories)
    print(player_wins)

    # Update agents here
