import rlcard
from rlcard.agents.random_agent import RandomAgent
from rlcard.rewarders.doudizhu import DoudizhuRewarder as Rewarder
# Example of using doudizhu environment
#from rlcard.envs.doudizhu import DoudizhuEnv

# make environment
env = rlcard.make('doudizhu')

print ('############## Environment of Doudizhu Initilized ################')


# set agents
agent_0 = RandomAgent()
agent_1 = RandomAgent()
agent_2 = RandomAgent()
env.set_agents([agent_0, agent_1, agent_2])

# set rewarder
rewarder = Rewarder()
env.set_rewarder(rewarder)

# seed everything
env.set_seed(0)
agent_0.set_seed(0)
agent_1.set_seed(0)
agent_2.set_seed(0)

for _ in range(1):
	# generate data from the environment
	trajectories = env.run()
	print(trajectories)

	# TODO
	# update agents
	# Input: trajectories