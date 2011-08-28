# -*- coding: utf-8 -*-

"""

msg.py - MIDI messages

"""

from __future__ import print_function, unicode_literals
from collections import OrderedDict, namedtuple
from .asserts import assert_time, assert_channel
from .asserts import assert_databyte, assert_songpos, assert_pitchwheel


msg_specs = {
  #
  # MIDI message specifications
  #
  # This is the authorative definition of message types.
  #

  #
  # Channel messages
  # 
  0x80 : ('note_off',     ('note',    'velocity'), 3),
  0x90 : ('note_on',      ('note',    'velocity'), 3),
  0xa0 : ('polytouch',    ('note',    'value'),    3),
  0xb0 : ('control',      ('number',  'value'),    3),
  0xc0 : ('program',      ('channel', 'number'),   3),
  0xd0 : ('aftertouch',   ('channel', 'value'),    3),
  0xe0 : ('pitchwheel',   ('channel', 'value'),    3),

  #
  # The value for pitchwheel is encoded as a 14 bit signed integer.
  # This is a pain to work with, si I convert it to a float in the
  # range [-1 ... 1]
  #   Todo: make conversion functions
  #

  #
  # System common messages
  #
  # songpos.pos is 14 bit unsigned,
  # seralized as lsb msb
  #
  # Todo: rename song to song_select?
  # 
  0xf0 : ('sysex',         ('vendor', 'data'), 2),
  0xf1 : ('undefined_f1',  (),                 1), 
  0xf2 : ('songpos',       ('pos', ),          3),  
  0xf3 : ('song',          ('song', ),         2),
  0xf4 : ('undefined_f4',  (), 1),
  0xf5 : ('undefined_f5',  (), 1),
  0xf6 : ('tune_request',  (), 1),
  0xf7 : ('sysex_end',     (), 1),

  #
  # System realtime messages These can interleave other messages but
  # they have no data bytes, so that's OK
  #

  0xf8 : ('clock',          (), 1),
  0xf9 : ('undefined_f9',   (), 1),
  0xfa : ('start',          (), 1),
  # Note: 'continue' is a keyword in python, so is
  # is bound to protomidi.msg.continue_
  0xfb : ('continue',       (), 1),
  0xfc : ('stop',           (), 1),
  0xfd : ('undefined_fd',   (), 1),
  0xde : ('active_sensing', (), 1),
  0xff : ('reset',          (), 1),
  }

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
        
        typeinfo = opcode2typeinfo[self.opcode]

        # Check keyword arguments to see
        # if any invalid names have been passed.
        # (Todo: rewrite that comment.)
        for name in override:
            if name not in self.typeinfo.names:
                msg = 'keyword argument for {} must be one of: {} (was {})'
                validnames = ' '.join(typeinfo.names)
                raise TypeError(msg.format(self.type,
                                           validnames,
                                           repr(name)))


        # Copy our values across,
        # letting the caller override
        # selected values.
        for name in typeinfo.names:
            if name in override:
                value = override[name]

                if name == 'time':
                    assert_time(value)

                elif name == 'channel':
                    assert_channel(value)

                elif msg.type == 'sysex' and name == 'data':
                    for byte in value:
                        assert_databyte(byte)
                    value = tuple(value)  # Convert to tuple
                    
                elif msg.type == 'pitchwheel' and name == 'value':
                    assert_pitchwheel(value)

                elif msg.type == 'songpos' and name == 'pos':
                    assert_songpos(value)

                else:
                    assert_databyte(value)

                ns[name] = value
            else:
                # Not overriden. Copy our value.
                ns[name] = getattr(self, name)

        return msg

    def __repr__(self):
        args = []
        for name in self._names:
            args.append('{0}={1}'.format(name,
                                         repr(getattr(self, name))))
        args = ', '.join(args)
            
        return '{0}({1})'.format(self.type, args)

    def __setattr__(self, name, value):
        raise ValueError('MIDI messages are immutable')

    def __delattr__(self, name):
        raise ValueError('MIDI messages are immutable')


__all__ = []

TypeInfo = namedtuple('TypeInfo', 'opcode type size names')
opcode2info = {}

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
    for opcode in msg_specs:
        (type, names, size) = msg_specs[opcode]

        msg = MIDIMessage()

        # Get name space
        ns = msg.__dict__

        # Fill in metadata
        ns['opcode'] = opcode
        ns['type'] = type
       
        if opcode < 0xf0:
            ns['channel'] = 0
            names = ('channel',) + names
 
        # Set data
        for name in names:
            if name == 'data':
                # Sysex needs special handling, as always
                ns[name] = ()
            else:
                ns[name] = 0

        info = TypeInfo(opcode=opcode,
                        type=type,
                        size=size,
                        names=names)

        if hasattr(msg, 'channel'):
            # Channel messages have 16 opcodes,
            # one for each MIDI channel.
            for channel in range(16):
                opcode2msg[msg.opcode|channel] = msg(channel=channel)
                opcode2info[opcode|channel] = info
        else:
            opcode2msg[msg.opcode] = msg
            opcode2info[opcode] = info

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
