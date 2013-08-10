import os
import imp
import types
import importlib
from .. import ports

import sys
import imp

def find_dotted_module(name, path=None):
    """Recursive version of imp.find_module.

    Handles dotted module names.
    """
    try:
        res = None
        for part in name.split('.'):
            res = imp.find_module(part, path)
            path = [res[1]]
        return res
    except ImportError:
        raise ImportError('No module named {}'.format(name))

class Backend(object):
    # Todo: doc strings.
    def __init__(self, module, load=False, use_environ=False, api=None):
        self.use_environ = use_environ

        if isinstance(module, types.ModuleType):
            self.name = module.__name__
            self._module = module
            self.api = api
        else:
            self.name = module
            self._module = None

            if '/' in self.name:
                self.name, self.api = self.name.split('/', 1)
                if self.api.strip() == '':
                    self.api = None
            else:
                self.api = None

            if self.name in sys.modules:
                self._module = sys.modules[self.name]
            elif not load:
                # Raise ImportError if module is not found.
                find_dotted_module(self.name)
            else:
                self.load()

        if api:
            self.api = api

    def _get_module(self):
        if not self._module:
            self.load()    
        return self._module

    def _fixkw(self, kwargs):
        if self.api and 'api' not in kwargs:
            kwargs['api'] = self.api
        return kwargs

    module = property(fget=_get_module)
    # del _get_module

    def load(self):
        if self._module is None:
            self._module = importlib.import_module(self.name)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def __getattr__(self, name):
        if name in ['Input', 'Output', 'IOPort', 'get_devices']:
            return getattr(self.module, name)
        else:
            raise AttributeError(name)

    def open_input(self, name=None, **kwargs):
        """Open an input port.

        If the environment variable MIDO_DEFAULT_INPUT is set,
        if will override the default port.
        """
        if name is None:
            name = self._env('MIDO_DEFAULT_INPUT')
        return self.module.Input(name, **self._fixkw(kwargs))

    def open_output(self, name=None, **kwargs):
        """Open an output port.
        
        If the environment variable MIDO_DEFAULT_OUTPUT is set,
        if will override the default port.
        """
        if name is None:
            name = self._env('MIDO_DEFAULT_OUTPUT')
        return self.module.Output(name, **self._fixkw(kwargs))

    def open_ioport(self, name=None, **kwargs):
        """Open a port for input and output.

        If the environment variable MIDO_DEFAULT_IOPORT is set,
        if will override the default port.
        """
        if name is None:
            name = self._env('MIDO_DEFAULT_IOPORT')
        if hasattr(self.module, 'IOPort'):
            if name is None:
                name = self._env('MIDO_DEFAULT_IOPORT')
            return self.module.IOPort(name, **self._fixkw(kwargs))
        else:
            if name is None:
                # MIDO_DEFAULT_IOPORT overrides the other two variables.
                name = self._env('MIDO_DEFAULT_IOPORT')
                if name is not None:
                    input_name = output_name = name
                else:
                    input_name = self._env('MIDO_DEFAULT_INPUT')
                    output_name = self._env('MIDO_DEFAULT_OUTPUT')
            else:
                input_name = output_name = name

            kwargs = self._fixkw(kwargs)
            return ports.IOPort(self.module.Input(input_name, **kwargs),
                                self.module.Output(output_name, **kwargs))

    def _get_devices(self, **kwargs):
        if hasattr(self.module, 'get_devices'):
            return self.module.get_devices(**self._fixkw(kwargs))
        else:
            return []

    def get_input_names(self, **kwargs):
        """Return a sorted list of all input port names."""
        devices = self._get_devices(**self._fixkw(kwargs))
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_output_names(self, **kwargs):
        """Return a sorted list of all output port names."""
        devices = self._get_devices(**self._fixkw(kwargs))
        names = [device['name'] for device in devices if device['is_output']]
        return list(sorted(names))

    def get_ioport_names(self, **kwargs):
        """Return a sorted list of all I/O port names."""
        devices = self._get_devices(**self._fixkw(kwargs))
        inputs = [device['name'] for device in devices if device['is_intput']]
        outputs = [device['name'] for device in devices if device['is_output']]
        return sorted(set(inputs) & set(outputs))

    def __getattr__(self, name):
        return getattr(self.module, name)

    def __repr__(self):
        if self._module is not None or self.name in sys.modules:
            status = 'loaded'
        else:
            status = 'not loaded'

        if self.api:
            name = '{}/{}'.format(self.name, self.api)
        else:
            name = self.name

        return '<backend {} ({})>'.format(name, status)
