"""
MIDI messages

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
MIN_PITCHWHEEL = -8192
MAX_PITCHWHEEL = 8191

# Song pos is a 14 bit unsigned integer
MIN_SONGPOS = 0
MAX_SONGPOS = 16383


class MsgSpec:
    """
    Specifications for creating a message.
    
    status_byte is the first byte of the message. For channel
    messages, the channel (lower 4 bits) is clear.

    type is the type name of the message, for example 'sysex'.

    args is the attributes / keywords arguments specific to
    this message type.

    size is the size of this message in bytes. This value is not used
    for sysex messages, since they use a top byte instead.
    """
    

    def __init__(self, status_byte, type_, args, size):
        """Create a new message specification.
        """
        self.status_byte = status_byte
        self.type = type_
        self.args = args
        self.size = size
    
    def signature(self):
        """Return call signature for Message constructor for this type.

        The signature is returned as a string.
        """
        parts = []
        parts.append(repr(self.type))

        for name in self.args:
            if name == 'data':
                parts.append('data=()')
            else:
                parts.append(name + '=0')
        parts.append('time=0')

        sig = '({})'.format(', '.join(parts))

        return sig


_MSG_SPECS = [
    #
    # MIDI message specifications
    #
    # This is the authorative definition of message types.
    #

    #
    # Each attribute name has a specific type and valid range.
    # Todo: This should be included in the documentation.
    #
    # 'channel'   0 - 15
    # 'control'   0 - 127
    # 'note'      0 - 127
    # 'program'   0 - 127
    # 'value'     0 - 127
    # 'velocity'  0 - 127
    # 'pitch'     MIN_PITCHWHEEL - MAX_PITCHWHEEL
    # 'pos'       MIN_SONGPOS - MAX_SONGPOS
    # 'data'      tuple of integers in range 0 - 127
    # 'time'      any number
    #

    #
    # Channel messages
    #
    # pitchwheel value is a signed integer in the range -8192 - 8191
    #
    MsgSpec(0x80, 'note_off',        ('channel', 'note',    'velocity'), 3),
    MsgSpec(0x90, 'note_on',         ('channel', 'note',    'velocity'), 3),
    MsgSpec(0xa0, 'polytouch',       ('channel', 'note',    'value'),    3),
    MsgSpec(0xb0, 'control_change',  ('channel', 'control', 'value'),    3),
    MsgSpec(0xc0, 'program_change',  ('channel', 'program',),   3),
    MsgSpec(0xd0, 'aftertouch',      ('channel', 'value',),    3),
    MsgSpec(0xe0, 'pitchwheel',      ('channel', 'pitch',),    3),

    #
    # System common messages
    #
    # songpos.pos is 14 bit unsigned int,
    # seralized as lsb msb
    #
    # Todo: rename song to song_select?
    #
    # Sysex messages have no fixed size. They instead use a stop byte
    # (0xf7, 'sysex_end') after the data bytes.
    #
    MsgSpec(0xf0, 'sysex',         ('data',),          None),
    MsgSpec(0xf1, 'undefined_f1',  (),                 1),
    MsgSpec(0xf2, 'songpos',       ('pos',),           3),
    MsgSpec(0xf3, 'song',          ('song',),          2),
    MsgSpec(0xf4, 'undefined_f4',  (), 1),
    MsgSpec(0xf5, 'undefined_f5',  (), 1),
    MsgSpec(0xf6, 'tune_request',  (), 1),
    MsgSpec(0xf7, 'sysex_end',     (), 1),

    #
    # System realtime messages. These can appear inside 'sysex'
    # messages.
    #
    MsgSpec(0xf8, 'clock',          (), 1),
    MsgSpec(0xf9, 'undefined_f9',   (), 1),
    MsgSpec(0xfa, 'start',          (), 1),
    # Note: 'continue' is a keyword in python, so is
    # is bound to protomidi.msg.continue_
    MsgSpec(0xfb, 'continue',       (), 1),
    MsgSpec(0xfc, 'stop',           (), 1),
    MsgSpec(0xfd, 'undefined_fd',   (), 1),
    MsgSpec(0xfe, 'active_sensing', (), 1),
    MsgSpec(0xff, 'reset',          (), 1),
]

#
# Dictionary for looking up Channel messages. This has keys
# for every valid message type name and for every valid status byte.
#
# For channel messages, there is one entry for each channel.
#
_SPEC_LOOKUP = {}  # Filled in by _init()

def assert_databyte(byte):
    """Raise ValueError if byte is not not int or out of range/

    Data bytes are 7 bit, so the valid range is 0 - 127.
    """

    if not (isinstance(byte, int) and (0 <= byte < 128)):
        raise ValueError('data byte must be and int in range 0 - 127.')


class Message(object):
    """
    MIDI message class.
    """

    # Attributes common to all messages.
    # These are used in __setattr__().
    _common_attrs = set(('spec', 'type', 'status_byte', 'time'))

    def __init__(self, type_, **kw):
        """Create a new message.

        The first argument is typically the type of message to create,
        for example 'note_on'.

        It can also be the status_byte, that is the first byte of the
        message. For channel messages, the channel (lower 4 bits of
        the status_byte) is masked out from the lower 4 bits of the
        status byte. This can be overriden by passing the 'channel'
        keyword argument.

        Valid keyword for each message type:

        Message('note_off', channel=0, note=0, velocity=0, time=0)
        Message('note_on', channel=0, note=0, velocity=0, time=0)
        Message('polytouch', channel=0, note=0, value=0, time=0)
        Message('control_change', channel=0, control=0, value=0, time=0)
        Message('program_change', channel=0, program=0, time=0)
        Message('aftertouch', channel=0, value=0, time=0)
        Message('pitchwheel', channel=0, pitch=0, time=0)
        Message('sysex', data=Message(), time=0)
        Message('undefined_f1', time=0)
        Message('songpos', pos=0, time=0)
        Message('song', song=0, time=0)
        Message('undefined_f4', time=0)
        Message('undefined_f5', time=0)
        Message('tune_request', time=0)
        Message('sysex_end', time=0)
        Message('clock', time=0)
        Message('undefined_f9', time=0)
        Message('start', time=0)
        Message('continue', time=0)
        Message('stop', time=0)
        Message('undefined_fd', time=0)
        Message('active_sensing', time=0)
        Message('reset', time=0)
        """
        

        try:
            spec = _SPEC_LOOKUP[type_]
        except KeyError:
            fmt = '{!r} is an invalid type name or status byte'
            raise ValueError(fmt.format(type_))

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
                if isinstance(type_, int):
                    self.channel = type_ & 0x0f
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
                    raise TypeError('time must be an integer or float')

            elif name == 'channel':
                if not isinstance(value, int):
                    raise TypeError('channel must be an integer')
                elif not 0 <= value < 16:
                    raise ValueError('channel must be in range 0 - 15')

            elif name == 'pos':
                if not isinstance(value, int):
                    raise TypeError('song pos must be and integer')
                elif not MIN_SONGPOS <= value <= MAX_SONGPOS:
                    s = 'song pos must be in range {} - {}'
                    raise ValueError(s.format(MIN_SONGPOS, MAX_SONGPOS))

            elif name == 'pitch':
                if not isinstance(value, int):
                    raise TypeError('pichwheel value must be an integer')
                elif not MIN_PITCHWHEEL <= value <= MAX_PITCHWHEEL:
                    s = 'pitchwheel value must be in range {} - {}'
                    raise ValueError(s.format(MIN_PITCHWHEEL,
                                              MAX_PITCHWHEEL))

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

            elif name == 'pitch':
                # Make pitch a positive number
                # by subtracting the minimum value.
                v = self.pitch - MIN_PITCHWHEEL
                b.append(v & 0x7f)  # LSB
                b.append(v >> 7)    # MSB

            elif name == 'pos':
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
