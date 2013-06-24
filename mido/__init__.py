# -*- coding: utf-8 -*-

"""
Mido - object oriented MIDI for Python

Create new objects (pydoc mido.new or help(mido.new)
for valid arguments):

   >>> mido.new('note_on', note=22, velocity=120)

Parsing and encoding messages:

   >>> msg = mido.parse([0x80, 0x23, 0x40])
   >>> msg = mido.parseall([0x90, 0x23, 0x40, [0x80, 0x23, 0x40]])
   

Ole Martin Bjørndalen
ombdalen@gmail.com
http://nerdly.info/ole/
"""

__author__ = 'Ole Martin Bjørndalen'
__email__ = 'ombdalen@gmail.com'
__url__ = 'http://nerdly.info/ole/'
__license__ = 'MIT'
__version__ = '0.0.0'

__all__ = []  # Prevent splat import

from .msg import Message
from .parser import Parser, parse, parseall
new = Message  # Shortcut
