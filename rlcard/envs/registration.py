import importlib

# Default Config
DEFAULT_CONFIG = {
        'allow_step_back': False,
        'seed': None,
        }

class EnvSpec(object):
    """A specification for a particular instance of the environment."""

    def __init__(self, env_id, entry_point=None):
        """
        Initialize

        Args:
            env_id (string): The name of the environment
            entry_point (string): A string the indicates the location of the environment class
        """
        self.env_id = env_id
        mod_name, class_name = entry_point.split(':')
        self._entry_point = getattr(importlib.import_module(mod_name), class_name)

    def make(self, config=None):
        """
        Instantiates an instance of the environment

        Returns:
            env (Env): An instance of the environment
            config (dict): A dictionary of the environment settings
        """
        if config is None:
            config = DEFAULT_CONFIG
        env = self._entry_point(config)
        return env


class EnvRegistry(object):
    """Register an environment (game) by ID"""

    def __init__(self):
        """Initialize"""
        self.env_specs = {}

    def register(self, env_id, entry_point):
        """
        Register an environment

        Args:
            env_id (string): The name of the environment
            entry_point (string): A string the indicates the location of the environment class
        """
        if env_id in self.env_specs:
            raise ValueError('Cannot re-register env_id: {}'.format(env_id))
        self.env_specs[env_id] = EnvSpec(env_id, entry_point)

    def make(self, env_id, config=None):
        """Create and environment instance

        Args:
            env_id (string): The name of the environment
            config (dict): A dictionary of the environment settings
        """
        if config is None:
            config = DEFAULT_CONFIG

        if env_id not in self.env_specs:
            raise ValueError('Cannot find env_id: {}'.format(env_id))

        return self.env_specs[env_id].make(config)


# Have a global registry
registry = EnvRegistry()


def register(env_id, entry_point):
    """Register an environment

    Args:
        env_id (string): The name of the environment
        entry_point (string): A string the indicates the location of the environment class
    """
    return registry.register(env_id, entry_point)


def make(env_id, config=None):
    """Create and environment instance

    Args:
        env_id (string): The name of the environment
        config (dict): A dictionary of the environment settings
    """
    if config is None:
        config = {}

    _config = DEFAULT_CONFIG.copy()

    for key in config:
        _config[key] = config[key]

    return registry.make(env_id, _config)
