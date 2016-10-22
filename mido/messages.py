"""
MIDI messages

There is no need to use this module directly. All you need is
available in the top level module.
"""
import sys

PY2 = (sys.version_info.major == 2)

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

    arguments is the attributes / keywords arguments specific to
    this message type.

    length is the length of this message in bytes. This value is not used
    for sysex messages, since they use an end byte instead.

    Table of MIDI messages:

        http://www.midi.org/techspecs/midimessages.php
    """

    def __init__(self, status_byte, type_, arguments, length):
        """Create a new message specification."""
        self.status_byte = status_byte
        self.type = type_
        self.arguments = arguments
        self.length = length
   
        # Attributes that can be set on the object
        self.settable_attributes = set(self.arguments) | {'time'}

    def signature(self):
        """Return call signature for Message constructor for this type.

        The signature is returned as a string.
        """
        parts = []
        parts.append(repr(self.type))

        for name in self.arguments:
            if name == 'data':
                parts.append('data=()')
            else:
                parts.append('{}=0'.format(name))
        parts.append('time=0')

        sig = '({})'.format(', '.join(parts))

        return sig


def get_message_specs():
    return [
        # Channel messages
        MessageSpec(0x80, 'note_off', ('channel', 'note', 'velocity'), 3),
        MessageSpec(0x90, 'note_on', ('channel', 'note', 'velocity'), 3),
        MessageSpec(0xa0, 'polytouch', ('channel', 'note', 'value'), 3),
        MessageSpec(0xb0, 'control_change',
                    ('channel', 'control', 'value'), 3),
        MessageSpec(0xc0, 'program_change', ('channel', 'program',), 2),
        MessageSpec(0xd0, 'aftertouch', ('channel', 'value',), 2),
        MessageSpec(0xe0, 'pitchwheel', ('channel', 'pitch',), 3),

        # System common messages
        MessageSpec(0xf0, 'sysex', ('data',), float('inf')),
        MessageSpec(0xf1, 'quarter_frame', ('frame_type', 'frame_value'), 2),
        MessageSpec(0xf2, 'songpos', ('pos',), 3),
        MessageSpec(0xf3, 'song_select', ('song',), 2),
        # 0xf4 is undefined.
        # 0xf5 is undefined.
        MessageSpec(0xf6, 'tune_request', (), 1),
        # 0xf7 is the stop byte for sysex messages, so should not be a message.

        # System real time messages
        MessageSpec(0xf8, 'clock', (), 1),
        # 0xf9 is undefined.
        MessageSpec(0xfa, 'start', (), 1),
        MessageSpec(0xfb, 'continue', (), 1),
        MessageSpec(0xfc, 'stop', (), 1),
        # 0xfd is undefined.
        MessageSpec(0xfe, 'active_sensing', (), 1),
        MessageSpec(0xff, 'reset', (), 1),
    ]


def build_spec_lookup(message_specs):
    lookup = {}

    for spec in message_specs:
        status_byte = spec.status_byte

        if status_byte < 0xf0:
            # Channel message.
            # The upper 4 bits are message type, and
            # the lower 4 are MIDI channel.
            # We need lookup for all 16 MIDI channels.
            for channel in range(16):
                lookup[status_byte | channel] = spec
        else:
            lookup[status_byte] = spec

        lookup[spec.type] = spec

    return lookup


def get_spec(type_or_status_byte):
    """Get message specification from status byte or message type name.

    For use in writing parsers.
    """
    try:
        return Message._spec_lookup[type_or_status_byte]
    except KeyError:
        raise LookupError('unknown type or status byte')


def check_time(time):
    """Check type and value of time.
    
    Raises TypeError if value is not an integer or a float
    """
    if PY2 and isinstance(time, long):
        return

    if not (isinstance(time, int) or isinstance(time, float)):
        raise TypeError('time must be an integer or float')


def check_channel(channel):
    """Check type and value of channel.

    Raises TypeError if the value is not an integer, and ValueError if
    it is outside range 0..15.
    """
    if not isinstance(channel, int):
        raise TypeError('channel must be an integer')
    elif not 0 <= channel <= 15:
        raise ValueError('channel must be in range 0..15')


def check_pos(pos):
    """Check type and value of song position.

    Raise TypeError if the value is not an integer, and ValueError if
    it is outside range MIN_SONGPOS..MAX_SONGPOS.
    """
    if not isinstance(pos, int):
        raise TypeError('song pos must be and integer')
    elif not MIN_SONGPOS <= pos <= MAX_SONGPOS:
        raise ValueError('song pos must be in range {}..{}'.format(
                         MIN_SONGPOS, MAX_SONGPOS))


def check_pitch(pitch):
    """Raise TypeError if the value is not an integer, and ValueError
    if it is outside range MIN_PITCHWHEEL..MAX_PITCHWHEEL.
    """
    if not isinstance(pitch, int):
        raise TypeError('pichwheel value must be an integer')
    elif not MIN_PITCHWHEEL <= pitch <= MAX_PITCHWHEEL:
        raise ValueError('pitchwheel value must be in range {}..{}'.format(
                         MIN_PITCHWHEEL, MAX_PITCHWHEEL))


def check_data(data_bytes):
    """Check type of data_byte and type and range of each data byte.

    Returns the data bytes as a SysexData object.

    Raises TypeError if value is not iterable.
    Raises TypeError if one of the bytes is not an integer.
    Raises ValueError if one of the bytes is out of range 0..127.
    """
    # Make the sequence immutable.
    data_bytes = SysexData(data_bytes)

    for byte in data_bytes:
        check_databyte(byte)

    return data_bytes


def check_frame_type(value):
    """Check type and value SMPTE quarter frame type.

    Raises TypeError if the value is not an integer.
    Raises ValueError if the value is out of range.
    """
    if not isinstance(value, int):
        raise TypeError('frame_type must be an integer')
    elif not 0 <= value <= 7:
        raise ValueError('frame_type must be in range 0..7')


def check_frame_value(value):
    """Check type and value of SMPTE quarter frame value.

    Raises TypeError if the value is not an integer.
    Raises ValueError if the value is out of range.
    """
    if not isinstance(value, int):
        raise TypeError('frame_value must be an integer')
    elif not 0 <= value <= 15:
        raise ValueError('frame_value must be in range 0..15')


def check_databyte(value):
    """Raise exception of byte has wrong type or is out of range

    Raises TypeError if the byte is not an integer, and ValueError if
    it is out of range. Data bytes are 7 bit, so the valid range is
    0..127.
    """
    if not isinstance(value, int):
        raise TypeError('data byte must be an integer')
    elif not 0 <= value <= 127:
        raise ValueError('data byte must be in range 0..127')


def encode_channel(channel):
    """Convert channel into a list of bytes. Return an empty list of
    bytes, since channel is already masked into status byte.
    """
    return []


def encode_data(data):
    """Encode sysex data as a list of bytes. A sysex end byte (0xf7)
    is appended.
    """
    return list(data) + [0xf7]

 
def encode_pitch(pitch):
    """Encode pitchwheel pitch as a list of bytes."""
    pitch -= MIN_PITCHWHEEL
    return [pitch & 0x7f, pitch >> 7]


def encode_pos(pos):
    """Encode song position as a list of bytes."""
    return [pos & 0x7f, pos >> 7]


class BaseMessage(object):
    """Base class for MIDI messages.

    Can be subclassed to create meta messages, for example.
    """
    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overridden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.

        Example:

            a = Message('note_on')
            b = a.copy(velocity=32)
        """

        # Make an exact copy of this object.
        klass = self.__class__
        msg = klass.__new__(klass)
        vars(msg).update(vars(self))

        for name, value in overrides.items():
            try:
                # setattr() is responsible for checking the
                # name and type of the attribute.
                setattr(msg, name, value)
            except AttributeError as err:
                raise ValueError(*err.args)

        return msg

    def bytes(self):
        raise ValueError('bytes() is not implemented in this class')

    def bin(self):
        """Encode message and return as a bytearray.

        This can be used to write the message to a file.
        """
        return bytearray(self.bytes())

    def hex(self, sep=' '):
        """Encode message and return as a string of hex numbers,

        Each number is separated by the string sep.
        """
        return sep.join('{:02X}'.format(byte) for byte in self.bytes())

    def __eq__(self, other):
        """Compare message to another for equality."""
        if not isinstance(other, BaseMessage):
            raise TypeError('comparison between message and another type')

        return vars(self) == vars(other)


class SysexData(tuple):
    """Special kind of tuple accepts and converts any sequence in +=."""
    def __iadd__(self, other):
        return SysexData(self + check_data(other))


class Message(BaseMessage):
    """
    MIDI message class.
    """

    # Quick lookup of specs by name or status_byte.
    _spec_lookup = build_spec_lookup(get_message_specs())

    # This is needed for __init__() so it doesn't accept status bytes.
    _type_lookup = {name: value for name, value in _spec_lookup.items() \
                        if not isinstance(name, int)}

    def __init__(self, type, **arguments):
        """Create a new message.

        The first argument is typically the type of message to create,
        for example 'note_on'.
        """
        try:
            spec = self._type_lookup[type]
        except KeyError:
            raise ValueError('invalid message type {!r}'.format(type))

        vars(self)['type'] = type
        vars(self)['_spec'] = spec

        # Set default values.
        for name in spec.arguments:
            if name == 'velocity':
                vars(self)['velocity'] = 0x40
            elif name == 'data':
                vars(self)['data'] = SysexData()
            else:
                vars(self)[name] = 0
        vars(self)['time'] = 0

        # Override defaults.
        for name, value in arguments.items():
            try:
                setattr(self, name, value)
            except AttributeError as err:
                raise ValueError(*err.args)

    def __setattr__(self, name, value):
        if name in self._spec.settable_attributes:
            try:
                if name == 'data':
                    value = check_data(value)
                else:
                    globals()['check_{}'.format(name)](value)
            except KeyError:
                check_databyte(value)

            vars(self)[name] = value
        elif name in vars(self):
            raise AttributeError('{} attribute is read only'.format(name))
        else:
            raise AttributeError(
                '{} message has no attribute {}'.format(self.type, name))

    def __delattr__(self, name):
        raise AttributeError('attribute cannot be deleted')

    def bytes(self):
        """Encode message and return as a list of integers."""

        status_byte = self._spec.status_byte
        if status_byte < 0xf0:
            # Add channel (lower 4 bits) to status byte.
            # Those bits in spec.status_byte are always 0.
            status_byte |= self.channel

        message_bytes = [status_byte]

        if self.type == 'quarter_frame':
            message_bytes.append(self.frame_type << 4 | self.frame_value)
        else:
            for name in self._spec.arguments:
                value = getattr(self, name)
                try:
                    encode = globals()['encode_{}'.format(name)]
                    message_bytes.extend(encode(value))
                except KeyError:
                    message_bytes.append(value)

        return message_bytes

    def __repr__(self):
        parts = []

        for name in self._spec.arguments + ('time',):
            parts.append('{}={!r}'.format(name, getattr(self, name)))

        return '<message {} {}>'.format(self.type, ' '.join(parts))

    def __str__(self):
        return format_as_string(self)

    def __len__(self):
        if self.type == 'sysex':
            return len(self.data) + 2
        else:
            return self._spec.length


def build_message(spec, bytes, time=0):
    """Build message from bytes.

    This is used by Parser and MidiFile. bytes is a full list
    of bytes for the message including the status byte. For sysex
    messages, the end byte is not included. Examples:

        build_message(spec, [0x80, 20, 100])
        build_message(spec, [0xf0, 1, 2, 3])

    No type or value checking is done, so you need to do that before
    you call this function. (This includes time.) 0xf7 is not allowed
    as status byte.
    """
    # This could be written in a more general way, but most messages
    # are note_on or note_off so doing it this way is faster.
    if spec.type in ['note_on', 'note_off']:
        attributes = {
                'channel': bytes[0] & 0x0f,
                'note': bytes[1],
                'velocity': bytes[2],
                }

    elif spec.type == 'control_change':
        attributes = {
                'channel': bytes[0] & 0x0f,
                'control': bytes[1],
                'value': bytes[2],
                }

    elif spec.status_byte < 0xf0:
        # Channel message. The most common type.
        if spec.type == 'pitchwheel':
            pitch = bytes[1] | ((bytes[2] << 7) + MIN_PITCHWHEEL)
            attributes = {'pitch': pitch}
        else:
            attributes = dict(zip(spec.arguments, bytes))
        # Replace status_bytes sneakily with channel.
        attributes['channel'] = bytes[0] & 0x0f

    elif spec.type == 'sysex':
        attributes = {'data': tuple(bytes[1:])}

    elif spec.type == 'songpos':
        pos = bytes[1] | (bytes[2] << 7)
        attributes = {'pos': pos}

    elif spec.type == 'quarter_frame':
        attributes = {'frame_type': bytes[1] >> 4,
                     'frame_value' : bytes[1] & 15}

    else:
        attributes = dict(zip(spec.arguments, bytes[1:]))

    # Message.__new__() is used as an optimization to
    # get around argument checking. We already know that
    # the values are valid.
    msg = Message.__new__(Message)
    vars(msg).update(attributes)
    vars(msg).update({
        'type': spec.type,
        '_spec': spec,
        'time': time,
    })
    return msg

def parse_time(text):
    if text.endswith('L'):
        raise ValueError('L is not allowed in time')

    if PY2:
        converters = [int, long, float]
    else:
        converters = [int, float]

    for convert in converters:
        try:
            return convert(text)
        except ValueError:
            pass

    raise ValueError('invalid format for time')


def parse_string(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    words = text.split()

    type_name = words[0]
    arguments = words[1:]

    names_seen = set()

    kwargs = {}

    for argument in arguments:
        try:
            name, value = argument.split('=')
        except ValueError:
            raise ValueError('missing or extraneous equals sign')

        if name in names_seen:
            raise ValueError('argument passed more than once')
        names_seen.add(name)

        if name == 'data':
            if not value.startswith('(') and value.endswith(')'):
                raise ValueError('missing parentheses in data message')

            try:
                data_bytes = [int(byte) for byte in value[1:-1].split(',')]
            except ValueError:
                raise ValueError('unable to parse data bytes')
            kwargs['data'] = data_bytes
        elif name == 'time':
            try:
                time = parse_time(value)
            except ValueError:
                raise ValueError('invalid value for time')
            try:
                kwargs['time'] = time
            except AttributeError as err:
                raise ValueError(err.message)
            except TypeError as err:
                raise ValueError(err.message)
        else:
            try:
                kwargs[name] = int(value)
            except AttributeError as exception:
                raise ValueError(*exception.args)
            except ValueError:
                raise ValueError('{!r} is not an integer'.format(value))

    return Message(type_name, **kwargs)


def parse_string_stream(stream):
    """Parse a stram of messages and yield (message, error_message)

    stream can be any iterable that generates text strings, where each
    string is a string encoded message.

    If a string can be parsed, (message, None) is returned. If it
    can't be parsed (None, error_message) is returned. The error
    message containes the line number where the error occurred.
    """
    line_number = 1
    for line in stream:
        try:
            line = line.split('#')[0].strip()
            if line:
                yield parse_string(line), None
        except ValueError as exception:
            error_message = 'line {line_number}: {message}'.format(
                line_number=line_number,
                message=exception.args[0])
            yield None, error_message
        line_number += 1


def format_as_string(message, include_time=True):
    """Format a message and return as a string.

    This is equivalent to str(message).

    To leave out the time attribute, pass include_time=False.
    """
    if not isinstance(message, Message):
        raise ValueError('message must be a mido.Message object')

    words = []
    words.append(message.type)

    names = message._spec.arguments
    if include_time:
        names += ('time',)

    for name in names:
        value = getattr(message, name)
        if name == 'data':
            value = '({})'.format(','.join(str(byte) for byte in value))
        elif name == 'time':
            # Python 2 formats longs as '983989385L'. This is not allowed.
            value = str(value)
            value = value.replace('L', '')
        words.append('{}={}'.format(name, value))
    
    return ' '.join(words)
