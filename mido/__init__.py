# -*- coding: utf-8 -*-

"""
Mido - Object Oriented MIDI for Python

New messages are created with mido.new() or mido.Message(), which both
return a message object.

Module content:

    Message(type, **kw) -> Message
    new(type, **kw) -> Message    alias for Message()

    Parser()
    parse(data) -> Message or None
    parse_all(data) -> [Message, ...]

type is type name or status byte.
byte is an integer in range 0 .. 255.
data is any sequence of bytes, or an object that generates them.

Se mido.portmidi for more about input and output ports.

For more on MIDI, see:

    http://midi.org/


Getting started:

    >>> import mido
    >>> msg = mido.new('note_on', channel=7, note=60, velocity=72)
    >>> msg.type
    'note_on'
    >>> msg.note = 4
    >>> msg.velocity += 3
    >>> msg
    mido.Message('note_on', channel=7, note=4, velocity=75, time=0)
    >>> msg.copy(note=22, time=1.23)
    mido.Message('note_on', channel=7, note=22, velocity=75, time=1.23)

    >>> sysex = mido.new('sysex')
    >>> sysex.data = range(3)
    >>> sysex.hex()
    'F0 00 01 02 F7'
"""

from . import ports, parser, messages
from .messages import Message
from .parser import Parser, parse, parse_all
new = Message  # Alias

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://github.com/olemb/mido/'
__license__ = 'MIT'
__version__ = '0.0.0'

# Prevent splat import.
__all__ = []

def input_names():
    """Return a sorted list of all input port names.
    These names can be passed to mido.input() and mido.port().
    """
    return _get_portmidi().get_input_names()


def output_names():
    """Return a sorted list of all output port names.
    These names can be passed to mido.output() and mido.port().
    """
    return _get_portmidi().get_output_names()


def port_names():
    """Return the names of all ports that axllow input and output."""
    return sorted(set(input_names()) & set(output_names()))


def input(name=None):
    """Open an input port."""
    return _open_port(name, mode='i')


def output(name=None):
    """Open an output port."""
    return _open_port(name, mode='o')


def port(name=None):
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
