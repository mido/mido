# SPDX-FileCopyrightText: 2014 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import importlib
import os
from typing import List

from .. import ports

DEFAULT_BACKEND = 'mido.backends.rtmidi'


class Backend:
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
            self._module = importlib.import_module(self.name)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def _add_api(self, kwargs):
        if self.api and 'api' not in kwargs:
            kwargs['api'] = self.api
        return kwargs

    def _get_devices(self, **kwargs):
        if hasattr(self.module, 'get_devices'):
            return self.module.get_devices(**self._add_api(kwargs))
        else:
            return []

    def __repr__(self):
        if self.loaded:
            status = 'loaded'
        else:
            status = 'not loaded'

        if self.api:
            name = f'{self.name}/{self.api}'
        else:
            name = self.name

        return f'<backend {name} ({status})>'

def set_backend(name=None, load=False):
    """Set current backend.

    name can be a module name like 'mido.backends.rtmidi' or
    a Backend object.

    If no name is passed, the default backend will be used.

    This will replace all the open_*() and get_*_name() functions
    in top level mido module. The module will be loaded the first
    time one of those functions is called.
    """
    glob = globals()

    if isinstance(name, Backend):
        backend = name
    else:
        backend = Backend(name, load=load, use_environ=True)
    glob['backend'] = backend

def get_current_backend() -> Backend:
    """Get actual backend.

    initiate it to default if not defined (should not be called
    because there is set_backend() in __init__.py)
    """
    glob = globals()
    _current_backend = glob['backend']
    if _current_backend is None:
        _current_backend = Backend(use_environ=True)
    return _current_backend

def open_input(name=None, virtual=False, callback=None, **kwargs):
    """Open an input port.

    If the environment variable MIDO_DEFAULT_INPUT is set,
    it will override the default port.

    virtual=False
        Passing True opens a new port that other applications can
        connect to. Raises IOError if not supported by the backend.

    callback=None
        A callback function to be called when a new message arrives.
        The function should take one argument (the message).
        Raises IOError if not supported by the backend.
    """
    backend = get_current_backend()
    kwargs.update(dict(virtual=virtual, callback=callback))

    if name is None:
        name = backend._env('MIDO_DEFAULT_INPUT')

    return backend.module.Input(name, **backend._add_api(kwargs))

def open_output(name=None, virtual=False, autoreset=False, **kwargs):
    """Open an output port.

    If the environment variable MIDO_DEFAULT_OUTPUT is set,
    it will override the default port.

    virtual=False
        Passing True opens a new port that other applications can
        connect to. Raises IOError if not supported by the backend.

    autoreset=False
        Automatically send all_notes_off and reset_all_controllers
        on all channels. This is the same as calling `port.reset()`.
    """
    backend = get_current_backend()
    kwargs.update(dict(virtual=virtual, autoreset=autoreset))

    if name is None:
        name = backend._env('MIDO_DEFAULT_OUTPUT')

    return backend.module.Output(name, **backend._add_api(kwargs))

def open_ioport(name=None, virtual=False,
                callback=None, autoreset=False, **kwargs):
    """Open a port for input and output.

    If the environment variable MIDO_DEFAULT_IOPORT is set,
    it will override the default port.

    virtual=False
        Passing True opens a new port that other applications can
        connect to. Raises IOError if not supported by the backend.

    callback=None
        A callback function to be called when a new message arrives.
        The function should take one argument (the message).
        Raises IOError if not supported by the backend.

    autoreset=False
        Automatically send all_notes_off and reset_all_controllers
        on all channels. This is the same as calling `port.reset()`.
    """
    backend = get_current_backend()
    kwargs.update(dict(virtual=virtual, callback=callback,
                        autoreset=autoreset))

    if name is None:
        name = backend._env('MIDO_DEFAULT_IOPORT') or None

    if hasattr(backend.module, 'IOPort'):
        # Backend has a native IOPort. Use it.
        return backend.module.IOPort(name, **backend._add_api(kwargs))
    else:
        # Backend has no native IOPort. Use the IOPort wrapper
        # in midi.ports.
        #
        # We need an input and an output name.

        # MIDO_DEFAULT_IOPORT overrides the other two variables.
        if name:
            input_name = output_name = name
        else:
            input_name = backend._env('MIDO_DEFAULT_INPUT')
            output_name = backend._env('MIDO_DEFAULT_OUTPUT')

        kwargs = backend._add_api(kwargs)

        return ports.IOPort(backend.module.Input(input_name, **kwargs),
                            backend.module.Output(output_name, **kwargs))

def get_input_names(**kwargs) -> List[str]:
    """Return a list of all input port names."""
    backend = get_current_backend()
    devices = backend._get_devices(**backend._add_api(kwargs))
    names = [device['name'] for device in devices if device['is_input']]
    return names

def get_output_names(**kwargs) -> List[str]:
    """Return a list of all output port names."""
    backend = get_current_backend()
    devices = backend._get_devices(**backend._add_api(kwargs))
    names = [device['name'] for device in devices if device['is_output']]
    return names

def get_ioport_names(**kwargs) -> List[str]:
    """Return a list of all I/O port names."""
    backend = get_current_backend()
    devices = backend._get_devices(**backend._add_api(kwargs))
    inputs = [device['name'] for device in devices if device['is_input']]
    outputs = {
        device['name'] for device in devices if device['is_output']}
    return [name for name in inputs if name in outputs]
