"""
msg.py - MIDI messages

New messages are created with mido.new() or mido.Message(),
which both return a message object.

MIDI messages are binary encoded as one status byte followed by zero
or more data bytes. The number and meaning of the data bytes is
specific to each message type. (The exception is System Exclusive
messages which have a start byte 0xf0 and end byte 0xf7 with any
number of data bytes inbetween.)

Data bytes are 7 bit, which means their values are in range 0 -
127. The high bit is set in status bytes to signal a new message.

A table of all standard MIDI messages and their binary encoding can be
found here:

   http://www.midi.org/techspecs/midimessages.php

"""

from __future__ import print_function
from collections import namedtuple


# Pitchwheel is a 14 bit signed integer
PITCHWHEEL_MIN = -8192
PITCHWHEEL_MAX = 8191


Spec = namedtuple('Spec', ('status_byte', 'type', 'args', 'size'))

_MSG_SPECS = [
    #
    # MIDI message specifications
    #
    # This is the authorative definition of message types.
    #

    #
    # Channel messages
    #
    # pitchwheel value is a signed integer in the range -8192 - 8191
    #
    Spec(0x80, 'note_off',        ('channel', 'note',    'velocity'), 3),
    Spec(0x90, 'note_on',         ('channel', 'note',    'velocity'), 3),
    Spec(0xa0, 'polytouch',       ('channel', 'note',    'value'),    3),
    Spec(0xb0, 'control_change',  ('channel', 'control', 'value'),    3),
    Spec(0xc0, 'program_change',  ('channel', 'program',),   3),
    Spec(0xd0, 'aftertouch',      ('channel', 'value',),    3),
    Spec(0xe0, 'pitchwheel',      ('channel', 'value',),    3),

    #
    # System common messages
    #
    # songpos.pos is 14 bit unsigned int,
    # seralized as lsb msb
    #
    # Todo: rename song to song_select?
    #
    # Sysex messages have a potentially infinite size.
    #
    Spec(0xf0, 'sysex',         ('data',),          float('inf')),
    Spec(0xf1, 'undefined_f1',  (),                 1),
    Spec(0xf2, 'songpos',       ('pos',),           3),
    Spec(0xf3, 'song',          ('song',),          2),
    Spec(0xf4, 'undefined_f4',  (), 1),
    Spec(0xf5, 'undefined_f5',  (), 1),
    Spec(0xf6, 'tune_request',  (), 1),
    Spec(0xf7, 'sysex_end',     (), 1),

    #
    # System realtime messages These can interleave other messages but
    # they have no data bytes, so that's OK
    #
    Spec(0xf8, 'clock',          (), 1),
    Spec(0xf9, 'undefined_f9',   (), 1),
    Spec(0xfa, 'start',          (), 1),
    # Note: 'continue' is a keyword in python, so is
    # is bound to protomidi.msg.continue_
    Spec(0xfb, 'continue',       (), 1),
    Spec(0xfc, 'stop',           (), 1),
    Spec(0xfd, 'undefined_fd',   (), 1),
    Spec(0xfe, 'active_sensing', (), 1),
    Spec(0xff, 'reset',          (), 1),
]

# Dictionary for looking up Channel messages have status byte keys for
# all channels. This means there are keys for all bytes in range
# range(128, 256).
_SPEC_LOOKUP = {}  # Filled in by _init()

def assert_databyte(byte):
    """Raise ValueError if byte is not not int or out of range/

    Data bytes are 7 bit, so the valid range is 0 - 127.
    """

    if not (isinstance(byte, int) and (0 <= byte < 128)):
        raise ValueError('data byte must be and int in range(0, 128)')


class Message(object):
    """
    MIDI message class.

    ('note_off', channel=0, note=0, velocity=0, time=0)
    ('note_on', channel=0, note=0, velocity=0, time=0)
    ('polytouch', channel=0, note=0, value=0, time=0)
    ('control_change', channel=0, control=0, value=0, time=0)
    ('program_change', channel=0, program=0, time=0)
    ('aftertouch', channel=0, value=0, time=0)
    ('pitchwheel', channel=0, value=0, time=0)
    ('sysex', data=(), time=0)
    ('undefined_f1', time=0)
    ('songpos', pos=0, time=0)
    ('song', song=0, time=0)
    ('undefined_f4', time=0)
    ('undefined_f5', time=0)
    ('tune_request', time=0)
    ('sysex_end', time=0)
    ('clock', time=0)
    ('undefined_f9', time=0)
    ('start', time=0)
    ('continue', time=0)
    ('stop', time=0)
    ('undefined_fd', time=0)
    ('active_sensing', time=0)
    ('reset', time=0)

    """

    # Attributes common to all messages.
    # These are used in __setattr__().
    _common_attrs = set(('spec', 'type', 'status_byte', 'time'))

    def __init__(self, type_or_status_byte, **kw):
        """Create a new message.

        The first argument determines the type, and for channel
        messages, the channel of the message.

        Each message type takes a specific set of keyword arguments.
        All values default to 0, except for

        Examples:
        
        Message('note_on', channel=7, note=3, velocity=0)

        
        """
        try:
            spec = _SPEC_LOOKUP[type_or_status_byte]
        except KeyError:
            fmt = '{!r} is an invalid type name or status byte'
            raise ValueError(fmt.format(type_or_status_byte))

        # Specify valid attributes for __setattr__().
        # (self._msg_attrs = set() wouldn't work here
        # since it's referred to by __setattr__()).
        self.__dict__['_msg_attrs'] = set(spec.args)
        
        self.spec = spec
        self.type = self.spec.type

        #
        # Set default values for attributes
        #
        self.time = 0
        for name in self.spec.args:
            if name == 'data':
                self.data = ()
            elif name == 'channel':
                # This is a channel message, so if the first
                # arguent to this function was a status_byte,
                # the lower 4 bits will contain the channel.
                if isinstance(type_or_status_byte, int):
                    self.channel = type_or_status_byte & 0x0f
                else:
                    self.channel = 0
            else:
                setattr(self, name, 0)

        #
        # Override attibutes with keyword arguments
        #
        for name, value in kw.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                fmt = '{!r} is an invalid keyword argument for this message'
                raise ValueError(fmt.format(name))

    def copy(self, **override):
        """Return a copy of the message.

        Attributes will be overriden by the passed keyword arguments.
        Only message specific attributes can be overriden. The message
        type can not be changed.

        Example:

            a = Message('note_on')
            b = a.copy(velocity=32)
        """
        # Get values from this object
        kw = {'time': self.time}
        for name in self.spec.args:
            kw[name] = getattr(self, name)

        # Override
        kw.update(override)

        return Message(self.type, **kw)

    def __setattr__(self, name, value):
        """Set an attribute."""
        if name in self._msg_attrs:
            if name == 'time':
                if not (isinstance(value, int) or isinstance(value, float)):
                    raise ValueError('time must be a number')

            elif name == 'channel':
                if not (isinstance(value, int) and (0 <= value < 16)):
                    raise ValueError('channel must be an int in range(0, 16)')

            elif name == 'pos':
                if not (isinstance(value, int) and (0 <= value < 32768)):
                    raise ValueError('pos must be an int in range(0, 32768)')

            elif name == 'value' and self.type == 'pitchwheel':
                if not (isinstance(value, int) and
                        (PITCHWHEEL_MIN <= value <= PITCHWHEEL_MAX)):
                    fmt = 'pitchwheel value must be an int in range({}, {})'
                    raise ValueError(fmt.format(PITCHWHEEL_MIN,
                                                PITCHWHEEL_MAX))

            elif name == 'data':
                value = tuple(value)  # Make the data bytes immutable
                for byte in value:
                    assert_databyte(byte)
            else:
                assert_databyte(value)

            # We can't assign directly here, or we'd have infinite
            # recursion.
            self.__dict__[name] = value
        elif name in self._common_attrs:
            self.__dict__[name] = value
        else:
            fmt = '{} message has no {!r} attribute'
            raise AttributeError(fmt.format(self.type, name))


    def __delattr__(self, name):
        raise AttributeError('Message attributes can\'t be deleted')

    def _get_status_byte(self):
        """Compute and return status byte.

        For channel messages, the returned status byte
        will contain the channel in its lower 4 bits.
        """
        # Add channel to status byte.
        sb = self.spec.status_byte
        if sb < 0xf0:
            sb |= self.channel
        return sb

    status_byte = property(fget=_get_status_byte)
    del _get_status_byte

    def bytes(self):
        """Encode message and return as a list of bytes (integers)."""
        b = [self.status_byte]

        for name in self.spec.args:
            if name == 'channel':
                continue  # We already have this

            elif name == 'data':
                b.extend(self.data)

            elif self.type == 'pitchwheel' and name == 'value':
                value = self.value + (2 ** 13)
                lsb = value & 0x7f
                msb = value >> 7
                b.append(lsb)
                b.append(msb)

            elif self.type == 'songpos' and name == 'pos':
                # Convert 14 bit value to two 7-bit values
                # Todo: check if this is correct
                lsb = self.pos & 0x7f
                b.append(lsb)

                msb = self.pos >> 7
                b.append(msb)
            else:
                # Ordinary data byte
                b.append(getattr(self, name))

        if self.type == 'sysex':
            # Append a sysex_end
            b.append(0xf7)

        return b

    def bin(self):
        """Encode message and return as a bytearray."""
        # Todo: bytearray() or bytes()
        return bytearray(self.bytes())

    def hex(self, sep=' '):
        """Encode message and return as a string of hex numbers,

        Each number is separated by the string sep.
        """
        return sep.join(['{:02X}'.format(byte) for byte in self.bytes()])

    def __repr__(self):
        args = [repr(self.type)]
        for name in self.spec.args:
            args.append('{}={!r}'.format(name, getattr(self, name)))
        args.append('time={!r}'.format(self.time))
        args = ', '.join(args)

        return 'mido.Message({})'.format(args)

    def __eq__(self, other):
        """Compare message to another for equality.
        
        Key for comparison: (msg.type, msg.channel, msg.note, msg.velocity).
        """
        if not isinstance(other, Message):
            raise TypeError('comparison between Message and another type')

        def key(msg):
            """Return a key for comparison."""
            k = tuple([msg.type] + [getattr(msg, a) for a in msg.spec.args])
            return k

        return key(self) == key(other)


def _build_signature(spec, include_type=True):
    """Return a constructor signature for this message type

    This is used to build documentation.
    """
    if include_type:
        parts = [repr(spec.type)]
    else:
        parts = []

    for name in spec.args + ('time',):
        if name == 'data':
            parts.append('data=()')
        else:
            parts.append(name + '=0')

    sig = '({})'.format(', '.join(parts))

    return sig


def _print_signatures():
    """Print valid arguments for mido.new() for all supported message types.

    This will be used to generate documentation.

    """
    for spec in _MSG_SPECS:
        sig = _build_signature(spec)
        print('mido.new {}'.format(sig))

def _init():
    """Initialize the module.

    This build a lookup table for message specs
    with keys for every valid message type and
    status byte.

    """
    for spec in _MSG_SPECS:
        if spec.status_byte < 0xf0:
            # Channel message.
            # The upper 4 bits are message type, and
            # the lower 4 are MIDI channel.
            # We need lookup for all 16 MIDI channels.
            for channel in range(16):
                _SPEC_LOOKUP[spec.status_byte | channel] = spec
        else:
            _SPEC_LOOKUP[spec.status_byte] = spec

        _SPEC_LOOKUP[spec.type] = spec

_init()
