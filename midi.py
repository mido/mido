# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import sys

"""
Ole Martin Bjørndalen
ombdalen@gmail.com
http://nerdly.info/ole/
"""

__author__ = 'Ole Martin Bjørndalen'
__license__ = 'MIT'

# Support Python 2 by overriding bytes() (but only in this module!)
if sys.version_info.major < 3:
    def bytes(byte_values):
        """Convert a list of byte values to a byte array (str)."""
        ret = b''
        for b in byte_values:
            ret += chr(b)
        return ret

def legal_data_byte(value):
    """Check if data byte is and integer in the range [0, 127], and return """

    if not isinstance(value, int):
        return False
    elif not 0 <= value <= 127:
        return False

    return True

def assert_data_byte(value):
    """Check if data byte is and int in in the correct range"""
    if not legal_data_byte(value):
        raise ValueError('MIDI data byte must an integer >= 0 and <= 127 (was %r)' % value)

def assert_time_value(time):
    """Check if time value is a number >= 0"""
    
    # Todo: there must be a better way to check this
    if not (isinstance(time, int) or (isinstance(time, float))) or time < 0:
        raise ValueError('MIDI time value must be a number >= 0 (was %r)' % time)

def is_chanmsg(msg):
    """Returns True if message is a channel message."""
    return msg.opcode < 0xf0

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
    def __init__(self, time=0, chan=0, note=0, vel=127):
        """Create a new MIDI message"""

        assert_time_value(time)
        [assert_data_byte(b) for b in [chan, note, vel]]

        self.time = time

        self.chan = chan
        self.note = note
        self.vel = vel

        # Serialize
        self.bytes = (self.opcode | self.chan, self.note, self.vel)
        self.bin = bytes(self.bytes)

    def copy(self, time=0, chan=0, note=0, vel=127):
        """Make a copy of the message, allowing caller to override selected values."""
        return self.__class__(time=time, chan=chan, note=note, vel=vel)

    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (self.type, self.time, self.chan, self.note, self.vel)

class note_on(note_off):
    opcode = 0x90
    type = 'note_on'

class sysex(midi_msg):
    """
    System exclusive message.
    """
    
    type = 'sysex'
    opcode = 0xf0

    def __init__(self, time=0, vendor=0, data=()):

        assert_time_value(time)
        assert_data_byte(vendor)
        [assert_data_byte(b) for b in data]

        self.time = time
        self.vendor = vendor
        self.data = tuple(data)

        # Serialize
        self.bytes = (self.opcode, self.vendor) + self.data
        self.bin = bytes(self.bytes)

    def copy(self, time=0, vendor=0, data=()):
        """Make a copy of the message, allowing caller to override selected values."""

        assert_time_value(time)
        assert_data_byte(vendor)
        [assert_data_byte(b) for b in data]

        return self.__class__(time=time, data=data)

    def __repr__(self):
        return '%s(time=%s, vendor=%s, data=%s)' % (self.type, self.time, self.vendor, self.data)

if __name__ == '__main__':
    on = note_on(note=60)
    off = note_off(note=60)
    sysex = sysex(vendor=7, data=(5, 6, 7, 3, 4, 4))

    print(on)
    print(on.copy(note=20))
    print(repr(on.bin))
    print(sysex)

# Prevent 'from midi import *' from pulluting namespace
# Use 'import midi' instead
__all__ = []
