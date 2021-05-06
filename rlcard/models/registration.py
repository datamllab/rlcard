import importlib

class ModelSpec(object):
    ''' A specification for a particular Model.
    '''
    def __init__(self, model_id, entry_point=None):
        ''' Initilize

        Args:
            model_id (string): the name of the model
            entry_point (string): a string that indicates the location of the model class
        '''
        self.model_id = model_id
        mod_name, class_name = entry_point.split(':')
        self._entry_point = getattr(importlib.import_module(mod_name), class_name)

    def load(self):
        ''' Instantiates an instance of the model

        Returns:
            Model (Model): an instance of the Model
        '''
        model = self._entry_point()
        return model


class ModelRegistry(object):
    ''' Register a model by ID
    '''

    def __init__(self):
        ''' Initilize
        '''
        self.model_specs = {}

    def register(self, model_id, entry_point):
        ''' Register an model

        Args:
            model_id (string): the name of the model
            entry_point (string): a string the indicates the location of the model class
        '''
        if model_id in self.model_specs:
            raise ValueError('Cannot re-register model_id: {}'.format(model_id))
        self.model_specs[model_id] = ModelSpec(model_id, entry_point)

    def load(self, model_id):
        ''' Create a model instance

        Args:
            model_id (string): the name of the model
        '''
        if model_id not in self.model_specs:
            raise ValueError('Cannot find model_id: {}'.format(model_id))
        return self.model_specs[model_id].load()

# Have a global registry
model_registry = ModelRegistry()


def register(model_id, entry_point):
    ''' Register a model

    Args:
        model_id (string): the name of the model
        entry_point (string): a string the indicates the location of the model class
    '''
    return model_registry.register(model_id, entry_point)

def load(model_id):
    ''' Create and model instance

    Args:
        model_id (string): the name of the model
    '''
    return model_registry.load(model_id)
