# -*- coding: utf-8 -*-

"""
Implements MIDI messages.

There is lot of boilerplate code to write to implement a message type,
but there's not a lot of information in a message. What's the most
compact notation that could be expanded into a working class (or
object)?

What's in a message

  opcode type [chan] [data]

how about this?

'''
  80 note_off    chan:4 note:7 vel:7
  90 note_on     chan:4 note:7 vel:7
  a0 polytouch   chan:4 note:7 value:7
  b0 control     chan:4 number:7 value:7
  c0 program     chan:4 program:7
  d0 aftertouch  chan:4 value:7
  c0 pitchwheel  chan:4 value:14-

  f0 sysex       vendor:7 data:7*
  f2 songpos     pos:14
  f3 song        song:7
  f6 tune_request
  f7 sysex_end

  f8 clock
  fa start
  fb continue
  fc stop
  fe active_sensing
  ff reset
'''

The types are:

  :4    4 bit unsigned int
  :7    7 bit unsigned int
  :14   15 bit unsigned int
  :14-  15 bit signed int
  :7*   0 or more 7 bit unsigned ints
"""

from __future__ import print_function, unicode_literals
import sys
from .types import *


# Support Python 2 by overriding bytes() (but only in this module!)
if sys.version_info.major < 3:
    def bytes(byte_values):
        """Convert a list of byte values to a byte array (str)."""
        ret = b''
        for b in byte_values:
            ret += chr(b)
        return ret


# Todo: use abc? 
class midi_msg:
    """
    Abstract base class for MIDI messages
    """
    def __len__(self):
        """Returns number of bytes in the message"""
        return len(self.bytes)


class note_off(midi_msg):
    """
    Class for note_on MIDI messages.
        
    Todo: Should use descriptors to ensure correct values
    and handle conversion of two-byte values to more meaningful types.
    
    The 'pitch_wheel' message could even have a descriptor which
    acesses the 'hi' and 'lo' bytes as a float in the range -1 .. 1
    """
    # Todo: is there a way to inspect the name of the current class here?
    opcode = 0x80
    type = 'note_off'

    #
    # Todo: there are essentially two contructors here. Use a function
    # instead, and have just one message class, and set __call__() to
    # a function with a closure on the message object?
    #
    #
    # Using shorter names 'chan' and 'vel' here. Don't know
    # if I'll stick with that.
    #
    def __init__(self, time=0, chan=0, note=0, vel=0):
        """Create a new MIDI message"""

        assert_time(time)
        assert_4bit(chan)
        assert_7bit(note, vel)

        self.time = time
        self.chan = chan
        self.note = note
        self.vel = vel

        # Serialize
        self.bytes = (self.opcode | self.chan, self.note, self.vel)
        self.bin = bytes(self.bytes)

    def copy(self, time=0, chan=0, note=0, vel=0):
        """Make a copy of the message, allowing caller to override selected values."""
        return self.__class__(time=time, chan=chan, note=note, vel=vel)

    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (self.type, self.time, self.chan, self.note, self.vel)


class note_on(note_off):
    opcode = 0x90
    type = 'note_on'


class aftertouch(midi_msg):
    opcode = 0x90
    type = 'aftertouch'

    def __init__(self, time=0, chan=0, note=0, value=0):
        
        assert_time(time)
        assert_4bit(chan)
        assert_7bit(note, value)

        self.time = time
        self.chan = chan
        self.note = note
        self.value = value

        # Serialize
        self.bytes = (self.opcode, self.vendor) + self.data
        self.bin = bytes(self.bytes)

    def __init__(self):
        return self.__class__(time=self.time, chan=self.chan, note=self.note, value=self.value)


class sysex(midi_msg):
    """
    System exclusive message.
    """
    
    type = 'sysex'
    opcode = 0xf0

    def __init__(self, time=0, vendor=0, data=()):

        assert_time(time)
        assert_7bit(vendor)
        assert_7bit(*data)

        self.time = time
        self.vendor = vendor
        self.data = tuple(data)

        # Serialize
        self.bytes = (self.opcode, self.vendor) + self.data
        self.bin = bytes(self.bytes)

    def copy(self, time=0, vendor=0, data=()):
        """Make a copy of the message, allowing caller to override selected values."""
        return self.__class__(time=time, data=data)

    def __repr__(self):
        return '%s(time=%s, vendor=%s, data=%s)' % (self.type, self.time, self.vendor, self.data)

# Make this splat import safe
__all__ = [ 'note_off',
            'note_on',
            'aftertouch',
            'sysex' ]
