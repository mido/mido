# -*- coding: utf-8 -*-

"""
msg.py - MIDI messages

Ole Martin Bjørndalen
ombdalen@gmail.com
http://nerdly.info/ole/

License: MIT

"""

from __future__ import print_function, unicode_literals
from collections import OrderedDict
from .asserts import assert_time, assert_channel, assert_data, assert_songpos, assert_pitchwheel


msg_specs = [
  #
  # MIDI message specifications
  #
  # This is the authorative definition of message types.
  #

  #
  # Channel messages
  # 
  'note_off     0x80|channel note velocity',
  'note_on      0x90|channel note velocity',
  'polytouch    0xa0|channel note value',     # what some call polypressure
  'control      0xb0|channel number value',   # control channelge
  'program      0xc0|channel number',         # program channelge
  'aftertouch   0xd0|channel value',          # what some call pressure
  'pitchwheel   0xe0|channel value',          # seralized as lsb msb

  #
  # The value for pitchwheel is encoded as a 14 bit signed integer.
  # This is a pain to work with, si I convert it to a float in the
  # range [-1 ... 1]
  #   Todo: make conversion functions
  #

  #
  # System common messages
  #
  'sysex         0xf0 vendor data',    # This requires special handling everywhere
  'undefined_f1  0xf1', 
  'songpos       0xf2 pos',            # 14 bit unsigned, seralized as lsb msb
  'song          0xf3 song',           # song select
  'undefined_f4  0xf4',
  'undefined_f5  0xf5',
  'tune_request  0xf6',
  'sysex_end     0xf7',

  #
  # System realtime messages
  # These can interleave other messages
  # (= cut in line), but they have no
  # data bytes, so it's OK
  #
  'clock           0xf8',
  'undefined_f9    0xf9',
  'start           0xfa',

  # Note: 'continue' is a keyword in python, so is
  # is bound to protomidi.msg.continue_
  'continue        0xfb',
  'stop            0xfc',
  'undefined_fd    0xfd',
  'active_sensing  0xfe',
  'reset           0xff',
  ]

class MIDIMessage:
    """
    A MIDI message

    MIDIMessage has no contructor, because it is always
    created by someone else: either by bootstrap() or
    by the __call__() method of the message it is cloned
    from.

    It is easier to have the message start or blank
    and have the caller fill it in, than to pass a
    lot of values and try to figure out where they
    should go.

    It's a bit unusual to have an object that only
    has a contructor for other objects, but it makes
    perfect sense here.

    MIDI messages are immutable, so their attributes
    must be set through __dict__.
    """

    def __call__(self, **override):
        """
        Create a new message based on ourself.
        The caller can override values.
        """

        # No keyword arguments?
        # Just return ourself.
        if not override:
            return self

        # Create a blank MIDI message
        msg = MIDIMessage()

        # Get the name space of the message
        ns = msg.__dict__

        # Copy metadata
        ns['opcode'] = self.opcode
        ns['type'] = self.type
        ns['names'] = self.names
        
        # Check keyword arguments to see
        # if any invalid names have been passed.
        # (Todo: rewrite that comment.)
        for name in override:
            if name not in self.names:
                msg = 'keyword argument for {} must be one of: {} (was {})'
                validnames = ' '.join(self.names)
                raise TypeError(msg.format(self.type,
                                           validnames,
                                           repr(name)))


        # Copy our values across,
        # letting the caller override
        # selected values.
        for name in self.names:
            if name in override:
                value = override[name]

                # print(msg.type, name, value)

                if name == 'time':
                    assert_time(value)

                elif name == 'channel':
                    assert_channel(value)

                elif name == 'data':
                    for byte in value:
                        assert_data(byte)
                    value = tuple(value)  # Convert to tuple
                    
                elif name == 'value' and type == 'pitchwheel':
                    assert_pitchwheel(value)

                elif name == 'pos':
                    assert_songpos(value)

                else:
                    assert_data(value)

                ns[name] = value
            else:
                # Not overriden. Copy our value.
                ns[name] = getattr(self, name)

        return msg

    def __repr__(self):
        args = []
        for name in self.names:
            args.append('{0}={1}'.format(name,
                                         repr(getattr(self, name))))
        args = ', '.join(args)
            
        return '{0}({1})'.format(self.type, args)

    def __setattr__(self, name, value):
        raise ValueError('MIDI messages are immutable')

    def __delattr__(self, name):
        raise ValueError('MIDI messages are immutable')

prototypes = {}
__all__ = []

def bootstrap(specline):
    """
    Bootstrap object cloning chain by creating an object from
    a specline.

    You can use this to implement previously undefined opcodes like
    0xf4, with the limitation that they can only contain byte values,
    since 14-bit values and systex data are handled by special cases
    in the code.
    """

    # Split line
    words = specline.split()
    type = words[0]
    args = words[2:]
    
    # Split 'opcode|channel'?
    opcode = words[1]
    if '|' in opcode:
        (opcode, arg) = opcode.split('|', 1)

        # prepend channel to arguments
        args.insert(0, arg)

    # Parse opcode
    opcode = int(opcode, base=16)

    #
    # Create the initial object of this type.
    #
    msg = MIDIMessage()

    # Get name space
    ns = msg.__dict__

    # Fill in metadata
    ns['opcode'] = opcode
    ns['type'] = type
    ns['names'] = args

    # Set data
    for arg in args:
        if arg == 'data':
            # Sysex needs special handling, as always
            ns[arg] = ()
        else:
            ns[arg] = 0

    return msg

#
# A mapping of
#
messages = {}

def _init():
    """
    Set up the initial objects in the clone chain.

    Also bind the objects to the top scope of this module, and
    put their names in __all__ so they can be splat-imported
    without polluting the name space with all that other gruff.
    """

    #
    # Create initial messages
    #
    for specline in msg_specs:
        msg = bootstrap(specline)
        if hasattr(msg, 'channel'):
            # Channel messages have 16 opcodes,
            # one for each MIDI channel.
            for channel in range(16):
                messages[msg.opcode|channel] = msg(channel=channel)
        else:
            messages[msg.opcode] = msg

        #
        # Bind to global scope (top of module)
        #
        if msg.type == 'continue':
            # Continue is a keyword in Python.
            # We need to add an underscore
            # to get around this.
            bindname = msg.type + '_'
        else:
            bindname = msg.type

        globals()[bindname] = msg

        #
        # Add to __all__
        #
        __all__.append(bindname)

_init()
