import importlib


class EnvSpec(object):
	"""A specification for a particular instance of the environment.
	"""

	def __init__(self, id, entry_point=None):
		""" Initilize

		Args:
			id (string): the name of the environent
			entry_point (string): a string the indicates the location of the envronment class
		"""


		self.id = id
		mod_name, class_name = entry_point.split(':')
		self._entry_point = getattr(importlib.import_module(mod_name), class_name)

	def make(self):
		"""Instantiates an instance of the environment

		Returns:
			env (Env): an instance of the environemnt
		"""

		env = self._entry_point()
		return env


class EnvRegistry(object):
	""" Register an environment (game) by ID
	"""

	def __init__(self):
		""" Initilize
		"""

		self.env_specs = {}

	def register(self, id, entry_point):
		""" Register an environment

		Args:
			id (string): the name of the environent
			entry_point (string): a string the indicates the location of the envronment class
		"""

		if id in self.env_specs:
			print ('Cannot re-register id: {}'.format(id))
		self.env_specs[id] = EnvSpec(id, entry_point)

	def make(self, id):
		""" Create and environment instance

		Args:
			id (string): the name of the environment
		"""

		if id not in self.env_specs:
			print ('Cannot find id: {}'.format(id))
		return self.env_specs[id].make()

# Have a global registry
registry = EnvRegistry()


def register(id, entry_point):
	""" Register an environment

	Args:
		id (string): the name of the environent
		entry_point (string): a string the indicates the location of the envronment class
	"""

    return registry.register(id, entry_point)

def make(id):
	""" Create and environment instance

	Args:
		id (string): the name of the environment
	"""
	
	return registry.make(id)



