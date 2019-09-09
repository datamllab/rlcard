# Example of using doudizhu environment
import rlcard
from rlcard.agents.random_agent import RandomAgent

# make environment
env = rlcard.make('doudizhu')

print('############## Environment of Doudizhu Initilized ################')

# set agents
agent_0 = RandomAgent(309)
agent_1 = RandomAgent(309)
agent_2 = RandomAgent(309)
env.set_agents([agent_0, agent_1, agent_2])

# seed everything

for _ in range(1):
	# TODO: add multi-process

	# generate data from the environment
	trajectories, player_wins = env.run(False)
	print(trajectories)
	print(player_wins)

	# Update agents here