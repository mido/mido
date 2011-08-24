from __future__ import print_function, unicode_literals

"""
An attempt to rewrite midi.py using named tuples (or something similar.

  - DRY (midi.py is notorious here)
  - MIDI messages should be immutable
  - the contructor must check if values are within range


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

#
# This could be auto-generated somehow from the list above# to avoid writing all that boilerplate.
#
# Using shorter names 'chan' and 'vel' here. Don't know
# if I'll stick with that.
#
class MidiMsg:
    """
    Abstract base class for MIDI messages
    """
    pass

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
    def __init__(self, time=0, chan=None, note=None, vel=None):
        """Create a new MIDI message"""

        assert_time_value(time)
        self.time = time

        if chan == None:
            self.chan = 0
        else:
            self.chan = chan
        
        if note == None:
            self.note = 0
        else:
            self.note = note

        if vel == None:
            self.vel = 127
        else:
            self.vel = vel

        # Serialize
        self.bytes = (self.opcode | self.chan, self.note, self.vel)

        # Todo: This will only work in Python >= 3
        self.bin = bytes(self.bytes)

        self._assert_values()

    def __call__(self, time=0, chan=None, note=None, vel=None):
        """Clone message, allowing caller to override selected values."""
        
        if time == None:
            time = self.time

        if chan == None:
            chan = self.chan

        if note == None:
            note = self.note

        if vel == None:
            vel = self.vel

        return NoteOn(time=time, chan=chan, note=note, vel=vel)

    def _assert_values(self):
        [assert_data_byte(b) for b in [self.chan, self.note, self.vel]]

    def __repr__(self):
        """Return a human-readable representation of the message"""
        return '%s(time=%s, chan=%s, note=%s, vel=%s)' % (self.type, self.time, self.chan, self.note, self.vel)

    def __str__(self):
        """Return message serialized to text"""
        return '%s %s  %s %s %s' % (self.time, self.type, self.chan, self.note, self.vel)

    def __len__(self):
        """Returns number of bytes in the message"""
        return len(self.bytes)

class NoteOn(NoteOff):
    opcode = 0x90
    type = 'note_on'

if __name__ == '__main__':
    on = NoteOn()
    off = NoteOff()

    print(on)
    print(on(note=20))
    print(on.bin)
