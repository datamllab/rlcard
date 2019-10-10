import importlib

class EnvSpec(object):
    ''' A specification for a particular instance of the environment.
    '''

    def __init__(self, env_id, entry_point=None):
        ''' Initilize

        Args:
            env_id (string): the name of the environent
            entry_point (string): a string the indicates the location of the envronment class
        '''
        self.env_id = env_id
        mod_name, class_name = entry_point.split(':')
        self._entry_point = getattr(importlib.import_module(mod_name), class_name)

    def make(self, allow_step_back=False):
        ''' Instantiates an instance of the environment

        Returns:
            env (Env): an instance of the environemnt
            allow_step_back (boolean): True if you wants to able to step_back
        '''
        env = self._entry_point(allow_step_back)
        return env


class EnvRegistry(object):
    ''' Register an environment (game) by ID
    '''

    def __init__(self):
        ''' Initilize
        '''
        self.env_specs = {}

    def register(self, env_id, entry_point):
        ''' Register an environment

        Args:
            env_id (string): the name of the environent
            entry_point (string): a string the indicates the location of the envronment class
        '''
        if env_id in self.env_specs:
            raise ValueError('Cannot re-register env_id: {}'.format(env_id))
        self.env_specs[env_id] = EnvSpec(env_id, entry_point)

    def make(self, env_id, allow_step_back=False):
        ''' Create and environment instance

        Args:
            env_id (string): the name of the environment
            allow_step_back (boolean): True if you wants to able to step_back
        '''
        if env_id not in self.env_specs:
            raise ValueError('Cannot find env_id: {}'.format(env_id))
        return self.env_specs[env_id].make(allow_step_back)

# Have a global registry
registry = EnvRegistry()


def register(env_id, entry_point):
    ''' Register an environment

    Args:
        env_id (string): the name of the environent
        entry_point (string): a string the indicates the location of the envronment class
    '''
    return registry.register(env_id, entry_point)

def make(env_id, allow_step_back=False):
    ''' Create and environment instance

    Args:
        env_id (string): the name of the environment
        allow_step_back (boolean): True if you wants to able to step_back
    '''
    return registry.make(env_id, allow_step_back)
