# -*- coding: utf-8 -*-

"""
Mido - object oriented MIDI for Python

Module content:

    Message(type, **kw) -> Message
    new(type, **kw) -> Message    alias for Message()

    parse(data) -> Message or None
    parseall(data) -> [Message, ...]

type is type name or status byte.
byte is an integer in range 0 - 255.
data is any sequence of bytes, or an object that generates them.
"""

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://github.com/olemb/mido/'
__license__ = 'MIT'
__version__ = '0.0.0'

from .msg import Message
from .parser import parse, parseall

new = Message  # Alias
