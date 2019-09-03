import random

class RandomAgent(object):
	""" 
	A random agent
	"""

	def __init__(self):
		pass

	def set_seed(self, seed):
		"""
			set seed
		"""
		random.seed(seed)


	def step(self, state):
            """
                    Randomly choose an action from the legal actions
            """
            actions = state['actions']
            return random.choice(actions)

