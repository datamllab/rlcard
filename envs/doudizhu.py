from rlcards.games.doudizhu import *
from rlcards.envs.env import env

class DoudizhuEnv(Env):
	"""
	Doudizhu Environment
	"""
	def __init__(self):
		self.game = Game()
		self.player_num = self.game.get_player_num() # get the number of players in the game


	def set_agents(self, agents):
		""" Set the agents that will interact with the environment

		Args:
			agents: list of Agent classes; [agents]
		self.agents = agents
		"""

		self.agents = agents

	def set_rewarder(self, rewarder):
		""" Set the agents that will interact with the environment

		Args:
			rewarder: Rewarder class
		self.agents = agents
		"""

		self.rewarder = rewarder

	def set_seed(self, seed):
		# TODO


	def run(self):
		# High level calls
		trajectories = [[] for _ in range(player_num)]

		# Loop to play the game
		player = self.game.get_player_id() # get the current player id
		state = self.game.get_state(player) # get the state of the first player
		trajectories[player].append(state)
		while not self.game.end():
			# First, agent plays
			action = self.agents[player].step(state)

			# Second, environment steps
			next_state, next_player = self.game.step(action)

			# Finally, save the data
			trajectories[player].append(action)
			trajectories[next_player].append(next_state)

			state = next_state
			palyer = next_player

		# Then the trajectories look like this:
		# trajectories[0] = [s_0, a_0, s_1, a_1, ...]

		# We reorganize the trajectories with the rewarder
		# And outout:
		# trajectories[0] = [[s, a, r, s']]

		# TODO: add reshaping with rewarder











