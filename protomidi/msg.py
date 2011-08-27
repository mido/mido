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
from asserts import assert_time, assert_channel, assert_data, assert_songpos, assert_pitchwheel

msg_specs = """
  #
  # MIDI message specifications
  #
  # This is the authorative definition of message types.
  #

  #
  # Channel messages
  # 
  note_off     0x80|channel note velocity
  note_on      0x90|channel note velocity
  polytouch    0xa0|channel note value     # what some call polypressure
  control      0xb0|channel number value   # control channelge
  program      0xc0|channel number         # program channelge
  aftertouch   0xd0|channel value          # what some call pressure
  pitchwheel   0xe0|channel value          # seralized as lsb msb

  #
  # The value for pitchwheel is encoded as a 14 bit signed integer.
  # This is a pain to work with, si I convert it to a float in the
  # range [-1 ... 1]
  #   Todo: make conversion functions
  #

  #
  # System common messages
  #
  sysex         0xf0 vendor data    # This requires special handling everywhere
  undefined     0xf1 
  songpos       0xf2 pos            # 14 bit unsigned, seralized as lsb msb
  song          0xf3 song           # song select
  undefined_f4  0xf4
  undefined_f5  0xf5
  tune_request  0xf6
  sysex_end     0xf7

  #
  # System realtime messages
  # These can interleave other messages
  # (= cut in line), but they have no
  # data bytes, so it's OK
  #
  clock           0xf8
  undefined_f9    0xf9
  start           0xfa

  # Note: 'continue' is a keyword in python, so is
  # is bound to protomidi.msg.continue_
  continue        0xfb
  stop            0xfc
  undefined_fd    0xfd
  active_sensing  0xfe
  reset           0xff
"""

__doc__ += msg_specs

class MIDIMessageSpec:
    """
    A MIDI message spec with the following attributes:

      name (string)
      opcode (int)
      args (list of strings)
    """

    def __init__(self, specline):
        words = specline.split()
        self.name = words[0]
        self.args = words[2:]

        # Split opcode|channel?
        opcode = words[1]
        if '|' in opcode:
            (opcode, argname) = opcode.split('|', 3)
            self.args.insert(0, argname)  # prepend channel
            # raise ValueError('syntax error in argspec (split opcode / channel): {}'.format(specline))

        self.opcode = int(opcode, base=16)
        
    def __repr__(self):
        return 'MIDIMessageSpec({})'.format(repr(self.specline))

class MIDIMessage:

    def __init__(self, spec):
        """
        Bootstrap MIDI message creation chain by creating an
        initial message object from a spec line.
        """
        #
        # Todo: Optimize - This should only need to be done once for each
        # message type.
        #

        if isinstance(spec, basestring):
            spec = MIDIMessageSpec(spec)

        # Get shortcut to namespace
        ns = self.__dict__

        #
        # Add metadata
        #
        ns['spec'] = spec
        ns['opcode'] = spec.opcode
        ns['type'] = spec.name
        ns['names'] = names = ['time'] + spec.args


        #
        # Add default data
        # Todo: this should only be done once per
        # message type. But where?
        #

        # Initialize all values to zero
        for name in names:
            ns[name] = 0

        # Initialize all data fields to 0
        zeroes = [0] * len(names)
        default_values = OrderedDict(zip(names, zeroes))

        # Sysex message need special care as always
        if 'data' in default_values:
            default_values['data'] = ns['date'] = ()

        #
        # Figure out how long we are.
        #
        length = 1  # we always have an opcode

        if 'data' in self.names:
            # Sysex messages require special handling,
            # as always.
            length += ns['data']
            length -= 1  # the reference to 'data' doesn't count

        if 'channel' in self.names:
            # Channel is stored in the opcode.
            length -= 1

        ns['_length'] = length

        # There we go
        self._update(default_values)

    def _update(self, kw):
        """
        Update data values. This is called by __call__()
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

            elif name == 'channel':
                assert_channel(value)

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

    def __len__(self):
        return self._length

    # def __cmp__():  # Todo: this is deprecated, so what do we do?
        
    def __call__(self, **kw):
        """
        Make a new message, using ourself as a prototype.
        Data values can be overriden by passing them as keyword
        arguments.
        """

        # No channelges, just return ourselves instead
        # of making a new object exacly like us.
        if not kw:
            return self

        ns = self.__dict__

        new = MIDIMessage(self.spec)

        # Copy our data
        values = {}
        for name in self.names:
            values[name] = ns[name]

        new._update(values)        
        new._update(kw)

        return new

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


#
# Maps opcode to message prototype
#
# Channelnel messages will have 16 entries each,
# one for each MIDI channelnel.
#
# Check if the byte is an opcode with midi.assert.isopcode()
# before you look it up here.
#
# Or you could use op2msg to check if a byte is an opcode.
#
#   if byte in op2msg:
#       # byte is an opcode
#
#    Todo: make it possible to override default message prototypes
#    (If anyone finds a use for all the undefined_xx messages.)
#
prototypes = {}
__all__ = []

def _make_message_prototypes(specs=msg_specs):

    """
    Create all MIDI message prototypes and bind them to the global
    scope (the midi.msg module).

    Also fills in prototypes and __all__
    """

    for line in specs.split('\n'):
        # Strip comments
        line = line.split('#')[0]

        # Strip whitespace
        line = line.strip()

        # Skip blank lines
        if not line:
            continue

        specline = line
        spec = MIDIMessageSpec(specline)
        msg = MIDIMessage(spec)


        bindname = msg.type
        # 'continue' is a keyword in Python
        # Get around this.
        if bindname == 'continue':
            bindname += '_'
        globals()[bindname] = msg
        
        #
        # Add prototype to __all__ to
        #     from protomidi.msg import *
        # works
        # 
        name = msg.type
        __all__.append(bindname)

        if hasattr(msg, 'channel'):
            #
            # Channelnel message need to be mapped to 16 different
            # opcodes each, one for each channelnel.
            #
            for channel in range(16):
                prototypes[msg.opcode | channel] = msg
        else:
            # System message have only one entry each
            prototypes[msg.opcode] = msg

prototypes = _make_message_prototypes()

if __name__ == '__main__':
    MIDI

