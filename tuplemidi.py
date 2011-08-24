"""
An attempt to rewrite midi.py using named tuples (or something similar.

  - DRY (midi.py is notorious here)
  - MIDI messages should be immutable
  - the contructor must check if values are within range

Example use:

    msg = note_on(channel=1, note=56, velocity=20)

All fields should have default values:

    msg = note_on(note=20)    

This can be accomplished using a prototope object, whose __call__()
method acts as a constructor, and who creates a new tuple with some
fields overriden by values passed to the constructor. You can then do:

    msg = note_on(note=24)
    msg = msg(channel=2)    # Update message
    msg = msg(note=10)

This may be a somewhat confusing syntax, but also very powerful.

The type of the message can not be changed. This means I can't use
collections.namedtuple.

There is no reason why messages should be tuples. The important thing
is that they are immutable.

Clearly, descriptors should be used.
"""

#
# Messages can be defined something like this
# (I need to check these values.)
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
}]

# Field specifiers
# The number after ':' is the number of bits used
'channel:4'    # four bit value (available in all channel messages)
'note:7'
'note:'        # 7 is the default size
'value:14'
'data:bytes'   # a tuple of byte values (on integer per byte)

Read only:

  - opcode / type
  - name

Read and update (by cloning):

  - all data values

__getitem__() access to the raw bytes.

len() returns length in bytes?
