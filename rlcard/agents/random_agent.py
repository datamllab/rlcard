import random

class RandomAgent(object):
	""" 
	A random agent
	"""

	def __init__(self, action_size):
		self.action_size = action_size

	def set_seed(self, seed):
		"""
			set seed
		"""
		random.seed(seed)


	def step(self, state):
            """
                    Randomly choose an action from the legal actions
            """
            return random.randint(0, self.action_size-1)

