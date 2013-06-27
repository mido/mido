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


class MessageSpec(object):
    """
    Specifications for creating a message.
    
    status_byte is the first byte of the message. For channel
    messages, the channel (lower 4 bits) is clear.

    type is the type name of the message, for example 'sysex'.

    args is the attributes / keywords arguments specific to
    this message type.

    size is the size of this message in bytes. This value is not used
    for sysex messages, since they use an end byte instead.
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


MESSAGE_SPECS = [
    # Channel messages
    MessageSpec(0x80, 'note_off', ('channel', 'note', 'velocity'), 3),
    MessageSpec(0x90, 'note_on', ('channel', 'note', 'velocity'), 3),
    MessageSpec(0xa0, 'polytouch', ('channel', 'note', 'value'), 3),
    MessageSpec(0xb0, 'control_change', ('channel', 'control', 'value'), 3),
    MessageSpec(0xc0, 'program_change', ('channel', 'program',), 3),
    MessageSpec(0xd0, 'aftertouch', ('channel', 'value',), 3),
    MessageSpec(0xe0, 'pitchwheel', ('channel', 'pitch',), 3),

    # System common messages
    MessageSpec(0xf0, 'sysex', ('data',), float('inf')),
    MessageSpec(0xf1, 'undefined_f1', (), 1),
    MessageSpec(0xf2, 'songpos', ('pos',), 3),
    MessageSpec(0xf3, 'song', ('song',), 2),
    MessageSpec(0xf4, 'undefined_f4', (), 1),
    MessageSpec(0xf5, 'undefined_f5', (), 1),
    MessageSpec(0xf6, 'tune_request', (), 1),
    MessageSpec(0xf7, 'sysex_end', (), 1),

    # System realtime messages
    MessageSpec(0xf8, 'clock', (), 1),
    MessageSpec(0xf9, 'undefined_f9', (), 1),
    MessageSpec(0xfa, 'start', (), 1),
    MessageSpec(0xfb, 'continue', (), 1),
    MessageSpec(0xfc, 'stop', (), 1),
    MessageSpec(0xfd, 'undefined_fd', (), 1),
    MessageSpec(0xfe, 'active_sensing', (), 1),
    MessageSpec(0xff, 'reset', (), 1),
]

#
# Dictionary for looking up Channel messages. This has keys
# for every valid message type name and for every valid status byte.
#
# For channel messages, there is one entry for each channel.
#
SPEC_LOOKUP = {}  # Filled in by _init()

def assert_databyte(byte):
    """Raise exception of byte has wrong type or is out of range

    Raises TypeError if the byte is not an integer, and ValueError if
    it is out of range. Data bytes are 7 bit, so the valid range is
    0 - 127.
    """

    if not isinstance(byte, int):
        raise TypeError('data byte must be an integer')
    elif not 0 <= byte <= 127:
        raise ValueError('data byte must be in range 0 - 127')


class Message(object):
    """
    MIDI message class.
    """

    # Attributes common to all messages.
    # These are used in __setattr__().
    _common_attributes = set(('spec', 'type', 'status_byte', 'time'))

    def __init__(self, type_, **args):
        """Create a new message.

        The first argument is typically the type of message to create,
        for example 'note_on'.

        It can also be the status_byte, that is the first byte of the
        message. For channel messages, the channel (lower 4 bits of
        the status_byte) is masked out from the lower 4 bits of the
        status byte. This can be overriden by passing the 'channel'
        keyword argument.
        """
        try:
            spec = SPEC_LOOKUP[type_]
        except KeyError:
            text = '{!r} is an invalid type name or status byte'
            raise ValueError(text.format(type_))

        # Specify valid attributes for __setattr__().
        # (self._msg_attributes = set() wouldn't work here
        # since it's referred to by __setattr__()).
        self.__dict__['_msg_attributes'] = set(spec.args)
        
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
        for name, value in args.items():
            try:
                setattr(self, name, value)
            except AttributeError:
                raise ValueError('{!r} is an invalid ' \
                                     'keyword argument for this message type' \
                                     ''.format(name))

    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overriden by the passed keyword arguments.
        Only message specific attributes can be overriden. The message
        type can not be changed.

        Example:

            a = Message('note_on')
            b = a.copy(velocity=32)
        """
        # Get values from this object
        args = {}
        for name in self.spec.args + ('time',):
            if name in overrides:
                args[name] = overrides[name]
            else:
                args[name] = getattr(self, name)

        return Message(self.type, **args)

    def __setattr__(self, name, value):
        """Set an attribute."""

        if name in self._msg_attributes:
            if name == 'time':
                if not (isinstance(value, int) or isinstance(value, float)):
                    raise TypeError('time must be an integer or float')

            elif name == 'channel':
                if not isinstance(value, int):
                    raise TypeError('channel must be an integer')
                elif not 0 <= value <= 15:
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
                # Make the data bytes immutable.
                # Raises TypeError if value is not iterable.
                value = tuple(value)
                for byte in value:
                    assert_databyte(byte)
            else:
                assert_databyte(value)

            # We can't assign directly here, or we'd have infinite
            # recursion.
            self.__dict__[name] = value
        elif name in self._common_attributes:
            self.__dict__[name] = value
        else:
            text = '{} message has no {!r} attribute'
            raise AttributeError(text.format(self.type, name))


    def __delattr__(self, name):
        raise AttributeError('Message attributes can\'t be deleted')

    def _get_status_byte(self):
        """Compute and return status byte.

        For channel messages, the returned status byte
        will contain the channel in its lower 4 bits.
        """
        byte = self.spec.status_byte
        if byte < 0xf0:
            # Add channel (lower 4 bits) to status byte.
            # Those bits in spec.status_byte are always 0.
            byte |= self.channel
        return byte

    status_byte = property(fget=_get_status_byte)
    del _get_status_byte

    def bytes(self):
        """Encode message and return as a list of bytes (integers)."""
        message_bytes = [self.status_byte]

        for name in self.spec.args:
            if name == 'channel':
                # This is a part of the status byte,
                # so we don't need to encode it here.
                continue

            elif name == 'data':
                message_bytes.extend(self.data)

            elif name == 'pitch':
                # Make pitch a positive number
                # by subtracting the minimum value.
                value = self.pitch - MIN_PITCHWHEEL
                message_bytes.append(value & 0x7f)  # Lower 7 bits
                message_bytes.append(value >> 7)    # Upper 7 bits

            elif name == 'pos':
                # Convert 14 bit value to two 7-bit values
                # Todo: check if this is correct
                message_bytes.append(self.pos & 0x7f)  # Lower 7 bit
                message_bytes.append(self.pos >> 7)    # Upper 7 bit
            else:
                # Ordinary data byte
                message_bytes.append(getattr(self, name))

        # Sysex messages need an end byte
        if self.type == 'sysex':
            message_bytes.append(0xf7)

        return message_bytes

    def bytearray(self):
        """Encode message and return as a bytearray.

        This can be used to write the message to a file.
        """
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
            return [msg.type] + [getattr(msg, arg) for arg in msg.spec.args]

        return key(self) == key(other)


def _initialize():
    """Initialize the module.

    This build a lookup table for message specs
    with keys for every valid message type and
    status byte.
    """
    for spec in MESSAGE_SPECS:
        if spec.status_byte < 0xf0:
            # Channel message.
            # The upper 4 bits are message type, and
            # the lower 4 are MIDI channel.
            # We need lookup for all 16 MIDI channels.
            for channel in range(16):
                SPEC_LOOKUP[spec.status_byte | channel] = spec
        else:
            SPEC_LOOKUP[spec.status_byte] = spec

        SPEC_LOOKUP[spec.type] = spec

_initialize()
