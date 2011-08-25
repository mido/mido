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
from asserts import assert_time, assert_chan, assert_data, assert_songpos, assert_pitchwheel

class Msg:

    def __init__(self, spec):
        """
        Bootstrap MIDI message creation chain by creating an
        initial message object from a spec line.
        """
        #
        # Todo: Optimize - This should only need to be done once for each
        # message type.
        #

        ns = self.__dict__

        words = spec.split()
        ns['spec'] = ' '.join(words)

        # Opcode
        ns['op'] = int(words[0], 16)
        ns['type'] = words[1]

        ns['names'] = names = ['time'] + words[2:]

        # Initialize all values to zero
        for name in names:
            ns[name] = 0

        # Initialize all data fields to 0
        default_values = OrderedDict(zip(names,
                                         [0]*len(names)))

        if 'data' in default_values:
            default_values['data'] = ()

        self._update(default_values)

    def _update(self, kw):
        """
        Update data values. This is called by copy()
        on the new object with the keword argument from
        the caller.
        """

        # Get shortcurt to namespace
        ns = self.__dict__

        for (name, value) in kw.items():
            if not name in self.names:
                msg = 'keyword argument for {} must be one of: {} (was {})'
                valid_names = ' '.join(self.names)
                raise TypeError(msg.format(self.type,
                                           valid_names,
                                           repr(name)))

            if name == 'time':
                assert_time(value)

            elif name == 'chan':
                assert_chan(value)

            elif name == 'data':
                for byte in value:
                    assert_data(byte)
                value = tuple(value)  # Convert to tuple

            elif name == 'pos':
                assert_songpos(value)

            elif name == 'value' and type == 'pitchwheel':
                assert_pitchwheel(value)

            else:
                assert_data(value)

            ns[name] = value

        
    def copy(self, **kw):
        """
        Make a clone of the message, with 0 or more data
        fields override.
        """

        ns = self.__dict__

        new = Msg(self.spec)

        # Copy our data
        values = {}
        for name in self.names:
            values[name] = ns[name]

        new._update(values)        
        new._update(kw)

        return new

    # This may be a little obscure, but oh so fun!
    __call__ = copy

    def __repr__(self):
        args = []
        for name in self.names:
            args.append('{0}={1}'.format(name,
                                       repr(getattr(self, name))))
        args = ', '.join(args)

        return '{0}({1})'.format(self.type, args)

    def __setattr__(self, name, value):
        raise ValueError('MIDI message object is immutable')

    def __delattr__(self, name):
        raise ValueError('MIDI message object is immutable')

msg_spec = """
  80 note_off    chan    note vel
  90 note_on     chan    note vel
  a0 polytouch   chan    note value
  b0 control     chan    number value
  c0 program     chan    program
  d0 aftertouch  chan    value
  e0 pitchwheel  chan    value

  f0 sysex          vendor data
  f1 undefined_f1
  f2 songpos        pos
  f3 song           song
  f4 undefined_f4
  f5 undefined_f5
  f6 tune_request
  f7 sysex_end

  f8 clock
  f9 undefined_f9
  fa start
  fb continue
  fc stop
  fd undefined_fd
  fe active_sensing
  ff reset
"""

#
# Maps opcode to message prototype
#
# Channel messages will have 16 entries each,
# one for each MIDI channel.
#
# Check if the byte is an opcode with midi.assert.isopcode()
# before you look it up here.
#
# Or you could use op2msg to check if a byte is an opcode.
#
#   if byte in op2msg:
#       # byte is an opcode
#
op2msg = {}
__all__ = []

def _make_message_prototypes(spec=msg_spec):

    """
    Create all MIDI message prototypes and bind them to the global
    scope (the midi.msg module).

    Also fills in op2msg and __all__
    """

    for line in spec.split('\n'):
        line = line.strip()

        # Skip blank lines
        if not line:
            continue

        msg = Msg(line)
        globals()[msg.type] = msg
        
        #
        # Add prototype to __all__ to
        #     from protomidi.msg import *
        # works
        # 
        name = msg.type
        # 'continue' is a keyword in Python
        # Get around this.
        if name == 'continue':
            name = name + '_'
        __all__.append(msg.type)

        if hasattr(msg, 'chan'):
            #
            # Channel message need to be mapped to 16 different
            # opcodes each, one for each channel.
            #
            for chan in range(16):
                op2msg[msg.op | chan] = msg
        else:
            # System message have only one entry each
            op2msg[msg.op] = msg

_make_message_prototypes()
