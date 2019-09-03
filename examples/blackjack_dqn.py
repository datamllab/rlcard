# Example of using doudizhu environment
import rlcard
from rlcard.agents.random_agent import RandomAgent


# make environment
env = rlcard.make('blackjack')

print('############## Environment of Doudizhu Initilized ################')

# set agents
agent_0 = RandomAgent()
env.set_agents([agent_0])

# seed everything
#env.set_seed(0)
#agent_0.set_seed(0)

for _ in range(1):
	# TODO: add multi-process

	# generate data from the environment
	trajectories, player_wins = env.run()
	print(trajectories)
	print(player_wins)

	# Update agents here
