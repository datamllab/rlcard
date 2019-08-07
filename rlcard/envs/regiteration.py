import importlib


class EnvSpec(object):
	"""A specification for a particular instance of the environment.
	"""

	def __init__(self, id, entry_point=None):
		self.id = id
		#self._entry_point = importlib.import_module(entry_point)
		mod_name, class_name = entry_point.split(':')
		self._entry_point = getattr(importlib.import_module(mod_name), class_name)

	def make(self):
		"""Instantiates an instance of the environment
		"""
		env = self._entry_point()
		return env


class EnvRegistry(object):
	""" Register an environment (game) by ID
	"""

	def __init__(self):
		self.env_specs = {}

	def register(self, id, entry_point):
		if id in self.env_specs:
			print ('Cannot re-register id: {}'.format(id))
		self.env_specs[id] = EnvSpec(id, entry_point)

	def make(self, id):
		if id not in self.env_specs:
			print ('Cannot find id: {}'.format(id))
		return self.env_specs[id].make()

# Have a global registry
registry = EnvRegistry()


def register(id, entry_point):
    return registry.register(id, entry_point)

def make(id):
	return registry.make(id)



