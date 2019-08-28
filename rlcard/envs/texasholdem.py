from rlcard.games.texasholdem import *
from rlcard.envs.env import Env
from rlcard.games.texasholdem.game import TexasGame as Game

import random

class TexasEnv(Env):
	"""
	Texasholdem Environment
	"""

	def test(self):
		print('aaa')

	def __init__(self):
		self.game = Game()
		self.player_num = self.game.get_player_num() # get the number of players in the game


	def set_agents(self, agents):
		""" Set the agents that will interact with the environment

		Args:
			agents: list of Agent classes; [agents]
		"""

		self.agents = agents

	def set_rewarder(self, rewarder):
		""" Set the agents that will interact with the environment

		Args:
			rewarder: Rewarder class
		"""

		self.rewarder = rewarder

	def set_seed(self, seed):
		random.seed(seed)
		print('############### seeded ############')


	def run(self):
		# High level calls
		trajectories = [[] for _ in range(self.player_num)]

		# Loop to play the game
		player = self.game.get_player_id() # get the current player id
		state = self.game.get_state(player) # get the state of the first player
		trajectories[player].append(state)
		while not self.game.end():
		#for i in range(6):
			# First, agent plays
			#print("### State:")
			#print(state)
			action = self.agents[player].step(state)


			# Second, environment steps
			next_state, next_player = self.game.step(action)

			# Finally, save the data
			#print(player, action, next_player)
			trajectories[player].append(action)
			if not self.game.end():
				trajectories[next_player].append(state)

			state = next_state
			player = next_player

		## add a final state to all the players
		for player in range(self.player_num):
			state = self.game.get_state(player)
			trajectories[player].append(state)














