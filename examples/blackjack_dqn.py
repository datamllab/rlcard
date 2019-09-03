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

#wins = 0

for _ in range(1000):
	# TODO: add multi-process

        
        # generate data from the environment
        trajectories, payoffs = env.run()
        print(trajectories)
        print(payoffs)
        #wins += payoffs[0]

        # Update agents here

print(wins)
