# -*- coding: utf-8 -*-

"""
MIDI Objects for Python

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

Creating messages:

    Message(type, **parameters) -- create a new message

Ports:

    open_input(name=None) -- open an input port
    open_output(name=None) -- open an output port
    open_ioport(name=None) -- open an I/O port (capable of both input
                                                and output)

    get_input_names() -- return a list of names of available input ports
    get_output_names() -- return a list of names of available output ports
    get_ioport_names() -- return a list of names of available I/O ports

Parsing MIDI streams:

    parse(bytes) -- parse a single message bytes
                    (any iterable that generates integers in 0..127)
    parse_all(bytes) -- parse all messages bytes
    Parser -- MIDI parser class

Parsing objects serialized with str(message):

    parse_string(string) -- parse a string containing a message
    parse_string_stream(iterable) -- parse strings from an iterable and
                                     generate messages

Sub modules:

    ports -- useful tools for working with ports

For more on MIDI, see:

    http://www.midi.org/


Getting started:

    >>> import mido
    >>> m = mido.Message('note_on', note=60, velocity=64)
    >>> m
    <note_on message channel=0, note=60, velocity=64, time=0>
    >>> m.type
    'note_on'
    >>> m.channel = 6
    >>> m.note = 19
    >>> m.copy(velocity=120)
    <note_on message channel=0, note=60, velocity=64, time=0>
    >>> s = mido.Message('sysex', data=[byte for byte in range(5)])
    >>> s.data
    (0, 1, 2, 3, 4)
    >>> s.hex()
    'F0 00 01 02 03 04 F7'
    >>> len(s)
    7

    >>> default_input = mido.open_input()
    >>> default_input.name
    'MPK mini MIDI 1'
    >>> output = mido.open_output('SD-20 Part A')
    >>>
    >>> for message in default_input:
    ...     output.send(message)

    >>> get_input_names()
    ['MPK mini MIDI 1', 'SH-201']
"""
from __future__ import absolute_import
import os
import importlib
from . import ports, sockets
from .messages import Message
from .messages import parse_string, parse_string_stream, format_as_string
from .parser import Parser, parse, parse_all

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://mido.readthedocs.org/'
__license__ = 'MIT'
__version__ = '1.0.0'

# Prevent splat import.
__all__ = []

class Backend(object):
    def __init__(self, path, on_demand=False, use_environ=False):
        self.path = path
        self.use_environ = use_environ

        self.module = None
        if not on_demand:
            self._import()

    def _import(self):
        if self.module is None:
            self.module = importlib.import_module(self.path)

    def _env(self, name):
        if self.use_environ:
            return os.environ.get(name)
        else:
            return None

    def open_input(self, name=None, **kwargs):
        """Open an input port.

        If the environment variable MIDO_DEFAULT_INPUT is set,
        if will override the default port.
        """
        self._import()
        if name is None:
            name = self._env('MIDO_DEFAULT_INPUT')
        return self.module.Input(name, **kwargs)

    def open_output(self, name=None, **kwargs):
        """Open an output port.
        
        If the environment variable MIDO_DEFAULT_OUTPUT is set,
        if will override the default port.
        """
        self._import()
        if name is None:
            name = self._env('MIDO_DEFAULT_OUTPUT')
        return self.module.Output(name, **kwargs)

    def open_ioport(self, name=None, **kwargs):
        """Open a port for input and output.

        If the environment variable MIDO_DEFAULT_IOPORT is set,
        if will override the default port.
        """
        self._import()

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

    def get_input_names(self):
        """Return a sorted list of all input port names."""
        self._import()
        devices = self.module.get_devices()
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_output_names(self):
        """Return a sorted list of all output port names."""
        self._import()
        devices = self.module.get_devices()
        names = [device['name'] for device in devices if device['is_input']]
        return list(sorted(names))

    def get_ioport_names(self):
        """Return a sorted list of all I/O port names."""
        self._import()
        return sorted(
            set(self.get_input_names()) & set(self.get_output_names()))        


def set_backend(path):
    """Set current backend.

    This will replace all the open_*() and get_*_name() functions
    in top level mido module. The module will be loaded the first
    time one of those functions is called."""

    glob = globals()

    backend = glob['backend'] = Backend(path, use_environ=True)
    for name in dir(backend):
        if name.split('_')[0] in ['open', 'get']:
            glob[name] = getattr(backend, name)


set_backend(os.environ.get('MIDO_BACKEND', 'mido.backends.portmidi'))
