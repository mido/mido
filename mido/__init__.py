# -*- coding: utf-8 -*-

"""
Mido - object oriented MIDI for Python

New messages are created with mido.new() or mido.Message(), which both
return a message object.

Module content:

    Message(type, **kw) -> Message
    new(type, **kw) -> Message    alias for Message()

    parse(data) -> Message or None
    parse_all(data) -> [Message, ...]

type is type name or status byte.
byte is an integer in range 0 - 255.
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

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://github.com/olemb/mido/'
__license__ = 'MIT'
__version__ = '0.0.0'

from .messages import Message
from .parser import parse, parse_all

new = Message  # Alias

__all__ = ['Message', 'parse', 'parse_all']
