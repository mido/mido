import os
import importlib
from .. import ports

DEFAULT_BACKEND = 'mido.backends.portmidi'

def _import_module(name):
    """Import and return module.

    This works like importlib._import_module(), except it handles
    packages without requiring and extra argument.

    Examples::

        _import_module('mido')
        _import_module('mido.backends.portmidi')
    """
    last_dot = name.rfind('.')
    if last_dot == -1:
        package, module = None, name
    else:
        package, module = name[:last_dot], name[last_dot:]

    try:
        return importlib.import_module(module, package)
    except ImportError:
        raise ImportError('No module named {}'.format(name))

class Backend(object):
    """
    Wrapper for backend module.

    A backend module implements classes for input and output ports for
    a specific MIDI library. The Backend object wraps around the
    object and provides convenient 'open_*()' and 'get_*_names()'
    functions.
    """
    def __init__(self, name=None, api=None, load=False, use_environ=True):
        self.name = name or os.environ.get('MIDO_BACKEND', DEFAULT_BACKEND)
        self.api = api
        self.use_environ = use_environ
        self._module = None

        # Split out api (if present).
        if api:
            self.api = api
        elif self.name and '/' in self.name:
            self.name, self.api = self.name.split('/', 1)
        else:
            self.api = None
            
        if load:
            self.load()

    @property
    def module(self):
        """A reference module implementing the backend.

        This will always be a valid reference to a module. Accessing
        this property will load the module. Use .loaded to check if
        the module is loaded.
        """
        self.load()
        return self._module

    @property
    def loaded(self):
        """Return True if the module is loaded."""
        return self._module is not None

    def load(self):
        """Load the module.

        Does nothing if the module is already loaded.
        
        This function will be called if you access the 'module'
        property."""
        if not self.loaded:
            self._module = _import_module(self.name)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def _fixkw(self, kwargs):
        if self.api and 'api' not in kwargs:
            kwargs['api'] = self.api
        return kwargs

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
        inputs = [device['name'] for device in devices if device['is_input']]
        outputs = [device['name'] for device in devices if device['is_output']]
        return sorted(set(inputs) & set(outputs))

    def __repr__(self):
        if self.loaded:
            status = 'loaded'
        else:
            status = 'not loaded'

        if self.api:
            name = '{}/{}'.format(self.name, self.api)
        else:
            name = self.name

        return '<backend {} ({})>'.format(name, status)
