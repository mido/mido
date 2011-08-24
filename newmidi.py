# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import sys

"""
An attempt to rewrite midi.py using named tuples (or something similar.

  - DRY (midi.py is notorious here)
  - MIDI messages should be immutable
  - MIDI messages should be pure data objects, with no methods other than
    __init__(), __call__(), __repr__(), __str__() and rich comparison
    operators. Utility functions will be used instead (midi.is_chanmsg() etc.)
  - the contructor must check if values are of the correct type and within range,
    so they can safely be serialized
  - serialized versions of the message is available in .bytes and .bin. One is
    an array of byte values as integers, the other is a byte array. I may change
    the names.
  - the Sysex message will have its data bytes stored as a tuple of integers


Read and update (by cloning):

  - all data values

__getitem__() access to the raw bytes.

len() returns length in bytes?

Ole Martin Bjørndalen
ombdalen@gmail.com
http://nerdly.info/ole/
"""

#
# Messages can be defined something like this
# (I need to check these values.)
#

#
# Todo:
#   - support rich comparisons (easy with self.bytes and self.bin)
#   - 
#

#
# Channel messages
#
channel_messages = [
    # Immutable                 Updatable (through cloning)
    # opcode  name
    (0x80, 'note_off',          'note velocity'),  
    (0x90, 'note_on',           'note velocity'),
    (0xa0, 'poly_pressure',     'note  pressure'),
    (0xb0, 'program_change',    'program'),
    (0xc0, 'control_change',    'control value'),
    (0xd0, 'channel_pressure',  'pressure'),
    (0xe0, 'pitch_wheel',       'value:14'),

    (),
]

# Field specifiers
# The number after ':' is the number of bits used
'channel:4'    # four bit value (available in all channel messages)
'note:7'
'note:'        # 7 is the default size
'value:14'
'data:bytes'   # a tuple of byte values (on integer per byte)

# Support Python 2
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
    """Check if data byte is and int in the range [0, 127], and raise ValueError if not"""
    if not legal_data_byte(value):
        raise ValueError('MIDI data byte must be an integer in the range [0, 127] (was %r)' % value)

def assert_time_value(time):
    """Check if time value is a number >= 0"""
    
    # Todo: there must be a better way to check this
    if not (isinstance(time, int) or (isinstance(time, float))) or time < 0:
        raise ValueError('MIDI time value must be a number >= 0')
 
class MidiMsg:
    """
    Abstract base class for MIDI messages
    """
    def __len__(self):
        """Returns number of bytes in the message"""
        return len(self.bytes)

class NoteOff(MidiMsg):
    """
    Class for NoteOn MIDI messages.
        
    Todo: Should use descriptors to ensure correct values
    and handle conversion of two-byte values to more meaningful types.
    
    The 'pitch_wheel' message could even have a descriptor which
    acesses the 'hi' and 'lo' bytes as a float in the range -1 .. 1
    """
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
    def __init__(self, time=0, chan=0, note=60, vel=127):
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

    def __call__(self, time=0, chan=0, note=60, vel=127):
        """Clone message, allowing caller to override selected values."""
        return NoteOn(time=time, chan=chan, note=note, vel=vel)

    def __repr__(self):
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (self.type, self.time, self.chan, self.note, self.vel)

    def __str__(self):
        """Return message serialized to text"""
        return '%s   %s   %s %s %s' % (self.time, self.type, self.chan, self.note, self.vel)

class NoteOn(NoteOff):
    type = 'note_on'
    opcode = 0x80

class Sysex(MidiMsg):
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

    def __call__(self, time=0, vendor=0, data=()):
        
        assert_time_value(time)
        assert_data_byte(vendor)
        [assert_data_byte(b) for b in data]

        return Sysex(time=time, data=data)

    def __repr__(self):
        return '%s(time=%s, vendor=%s, data=%s)' % (self.type, self.time, self.vendor, self.data)

    def __getitem__(self, i):
        return self.data[i]

    def __str__(self):
        """Return message serialized to text"""
        
        data = ' '.join([str(b) for b in self.bytes])
        return '%s   %s %s   %s' % (self.time, self.type, self.vendor, data)


note_on = NoteOn()
note_off = NoteOff()
sysex = Sysex()

class NoteOn(NoteOff):
    opcode = 0x90
    type = 'note_on'

if __name__ == '__main__':
    on = note_on()
    off = note_off()
    sysex = sysex(vendor=7, data=(5, 6, 7, 3, 4, 4))

    print(on)
    print(on(note=20))
    print(repr(on.bin))
    print(sysex)
