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
    def __init__(self, module, on_demand=True, use_environ=False):
        self.use_environ = use_environ

        if isinstance(module, types.ModuleType):
            self.name = module.__name__
            self.module = module
        else:
            self.name = module
            self.module = None

            if self.name in sys.modules:
                self.module = sys.modules[self.name]
            elif on_demand:
                find_dotted_module(self.name)
            else:
                self.load()

    def load(self):
        if self.module is None:
            self.module = importlib.import_module(self.name)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def __getattr__(self, name):
        if name in ['Input', 'Output', 'IOPort', 'get_devices']:
            self.load()
            return getattr(self.module, name)
        else:
            raise AttributeError(name)

    def open_input(self, name=None, **kwargs):
        """Open an input port.

        If the environment variable MIDO_DEFAULT_INPUT is set,
        if will override the default port.
        """
        self.load()
        if name is None:
            name = self._env('MIDO_DEFAULT_INPUT')
        return self.module.Input(name, **kwargs)

    def open_output(self, name=None, **kwargs):
        """Open an output port.
        
        If the environment variable MIDO_DEFAULT_OUTPUT is set,
        if will override the default port.
        """
        self.load()
        if name is None:
            name = self._env('MIDO_DEFAULT_OUTPUT')
        return self.module.Output(name, **kwargs)

    def open_ioport(self, name=None, **kwargs):
        """Open a port for input and output.

        If the environment variable MIDO_DEFAULT_IOPORT is set,
        if will override the default port.
        """
        self.load()

        if name is None:
            name = self._env('MIDO_DEFAULT_IOPORT')
        if hasattr(self.module, 'IOPort'):
            if name is None:
                name = self._env('MIDO_DEFAULT_IOPORT')
            return self.module.IOPort(name, **kwargs)
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

            return ports.IOPort(self.module.Input(input_name, **kwargs),
                                self.module.Output(output_name, **kwargs))

    def _get_devices(self):
        if hasattr(self.module, 'get_devices'):
            return self.module.get_devices()
        else:
            return []

    def get_input_names(self):
        """Return a sorted list of all input port names."""
        self.load()
        devices = self._get_devices()
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_output_names(self):
        """Return a sorted list of all output port names."""
        self.load()
        devices = self._get_devices()
        names = [device['name'] for device in devices if device['is_output']]
        return list(sorted(names))

    def get_ioport_names(self):
        """Return a sorted list of all I/O port names."""
        self.load()
        return sorted(
            set(self.get_input_names()) & set(self.get_output_names()))        

    def __repr__(self):
        if self.module is not None or self.name in sys.modules:
            status = 'loaded'
        else:
            status = 'not loaded'

        return '<backend {!r} ({})>'.format(self.name, status)
