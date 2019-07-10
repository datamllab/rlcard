import rlcards
import RandomAgent
import DefaultRewarder
# Example of using doudizhu environment

# make environment
env = rlcards.make('doudizhu')

# set agents (TODO: add example random agents)
agent_0 = RandomAgent()
agent_1 = RandomAgent()
agent_2 = RandomAgent()
env.set_agents([agent_0, agent_1, agent_2])

# set rewarder (TODO: add rewarder)
rewarder = DefaultRewarder()
env.set_rewarder(rewarder)

# set seed (optinal)
env.set_seed(0)

for _ in range(1000):
	# generate data from the environment
	trajectories = env.run()

	# TODO
	# update agents
	# Input: trajectories