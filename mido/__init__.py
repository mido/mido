# -*- coding: utf-8 -*-

"""
MIDI Objects for Python

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

Creating messages:

    new(type, **parameters) -- create a new message

Ports:

    input(name=None) -- open an input port
    output(name=None) -- open an output port
    ioport(name=None) -- open an I/O port (capable of both input and output)

    input_names() -- return a list of names of available input ports
    output_names() -- return a list of names of available output ports
    ioport_names() -- return a list of names of available I/O ports

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
    >>> m = mido.new('note_on', note=60, velocity=64)
    >>> m
    <note_on message channel=0, note=60, velocity=64, time=0>
    >>> m.type
    'note_on'
    >>> m.channel = 6
    >>> m.note = 19
    >>> m.copy(velocity=120)
    <note_on message channel=0, note=60, velocity=64, time=0>
    >>> s = mido.new('sysex', data=[byte for byte in range(5)])
    >>> s.data
    (0, 1, 2, 3, 4)
    >>> s.hex()
    'F0 00 01 02 03 04 F7'
    >>> len(s)
    7

    >>> default_input = mido.input()
    >>> default_input.name
    'MPK mini MIDI 1'
    >>> output = mido.output('SD-20 Part A')
    >>>
    >>> for message in default_input:
    ...     output.send(message)

    >>> input_names()
    ['MPK mini MIDI 1', 'SH-201']
"""
from . import ports
from .messages import Message, parse_string, parse_string_stream
from .parser import Parser, parse, parse_all

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://github.com/olemb/mido/'
__license__ = 'MIT'
__version__ = '0.0.0'

# Prevent splat import.
__all__ = []


def new(type, **parameters):
    """Return a new message.

    For a list of valid parameters, see the Message Types in the docs.
    """
    return Message(type, **parameters)


def input_names():
    """Return a sorted list of all input port names.
    These names can be passed to mido.input() and mido.port().
    """
    return _get_portmidi().input_names()


def output_names():
    """Return a sorted list of all output port names.
    These names can be passed to mido.output() and mido.port().
    """
    return _get_portmidi().output_names()


def ioport_names():
    """Return the names of all ports that axllow input and output."""
    return sorted(set(input_names()) & set(output_names()))


def input(name=None):
    """Open an input port."""
    return _open_port(name, mode='i')


def output(name=None):
    """Open an output port."""
    return _open_port(name, mode='o')


def ioport(name=None):
    """Open a port for input and output."""
    return _open_port(name, mode='io')


def _get_portmidi():
    # Todo: check for exceptions?
    from . import portmidi
    return portmidi


def _open_port(name=None, mode=None, backend='portmidi'):
    backend = _get_portmidi()

    if mode == 'i':
        return backend.Input(name)
    elif mode == 'o':
        return backend.Output(name)
    elif mode == 'io':
        return ports.IOPort(backend.Input(name),
                            backend.Output(name))
    else:
        raise ValueError('invalid mode {!r}'.format(mode))
