"""
Meta messages for MIDI files.

TODO:
     - what if an unknown meta message is implemented and someone depends on
       the 'data' attribute?
     - is 'type_byte' a good name?
     - 'values' is not a good name for a dictionary.
     - type and value safety?
     - copy().
     - expose _key_signature_encode/decode?
"""
from __future__ import print_function, division
import math
import struct
from numbers import Integral
from contextlib import contextmanager
from ..messages import BaseMessage, check_time
from ..py2 import PY2

_charset = 'latin1'


class KeySignatureError(Exception):
    """ Raised when key cannot be converted from key/mode to key letter """
    pass


def _reverse_table(table):
    """Return value: key for dictionary."""
    return {value: key for (key, value) in table.items()}


_key_signature_decode = {(-7, 0): 'Cb',
                         (-6, 0): 'Gb',
                         (-5, 0): 'Db',
                         (-4, 0): 'Ab',
                         (-3, 0): 'Eb',
                         (-2, 0): 'Bb',
                         (-1, 0): 'F',
                         (0, 0): 'C',
                         (1, 0): 'G',
                         (2, 0): 'D',
                         (3, 0): 'A',
                         (4, 0): 'E',
                         (5, 0): 'B',
                         (6, 0): 'F#',
                         (7, 0): 'C#',
                         (-7, 1): 'Abm',
                         (-6, 1): 'Ebm',
                         (-5, 1): 'Bbm',
                         (-4, 1): 'Fm',
                         (-3, 1): 'Cm',
                         (-2, 1): 'Gm',
                         (-1, 1): 'Dm',
                         (0, 1): 'Am',
                         (1, 1): 'Em',
                         (2, 1): 'Bm',
                         (3, 1): 'F#m',
                         (4, 1): 'C#m',
                         (5, 1): 'G#m',
                         (6, 1): 'D#m',
                         (7, 1): 'A#m',
                         }

_key_signature_encode = _reverse_table(_key_signature_decode)

_smpte_framerate_decode = {0: 24,
                           1: 25,
                           2: 29.97,
                           3: 30,
                           }

_smpte_framerate_encode = _reverse_table(_smpte_framerate_decode)


def signed(to_type, n):
    formats = {'byte': 'Bb',
               'short': 'Hh',
               'long': 'Ll',
               'ubyte': 'bB',
               'ushort': 'hH',
               'ulong': 'lL'
               }

    try:
        pack_format, unpack_format = formats[to_type]
    except KeyError:
        raise ValueError('invalid integer type {}'.format(to_type))

    try:
        packed = struct.pack(pack_format, n)
        return struct.unpack(unpack_format, packed)[0]
    except struct.error as err:
        raise ValueError(*err.args)


def unsigned(to_type, n):
    return signed('u{}'.format(to_type), n)


def encode_variable_int(value):
    """Encode variable length integer.

    Returns the integer as a list of bytes,
    where the last byte is < 128.

    This is used for delta times and meta message payload
    length.
    """
    if not isinstance(value, Integral) or value < 0:
        raise ValueError('variable int must be a positive integer')

    bytes = []
    while value:
        bytes.append(value & 0x7f)
        value >>= 7

    if bytes:
        bytes.reverse()

        # Set high bit in every byte but the last.
        for i in range(len(bytes) - 1):
            bytes[i] |= 0x80
        return bytes
    else:
        return [0]


def encode_string(string):
    return list(bytearray(string.encode(_charset)))


def decode_string(data):
    return bytearray(data).decode(_charset)


@contextmanager
def meta_charset(tmp_charset):
    global _charset
    old = _charset
    _charset = tmp_charset
    yield
    _charset = old


def check_int(value, low, high):
    if not isinstance(value, Integral):
        raise TypeError('attribute must be an integer')
    elif not low <= value <= high:
        raise ValueError('attribute must be in range {}..{}'.format(low, high))


if PY2:
    _STRING_TYPE = (str, unicode)  # noqa: F821
else:
    _STRING_TYPE = str


def check_str(value):
    if not isinstance(value, _STRING_TYPE):
        raise TypeError('attribute must be a string')


class MetaSpec(object):
    # The default is to do no checks.
    def check(self, name, value):
        pass


class MetaSpec_sequence_number(MetaSpec):
    type_byte = 0x00
    attributes = ['number']
    defaults = [0]

    def decode(self, message, data):
        if len(data) == 0:
            # Message with length 0 can occur in some files.
            # (See issues 42 and 93.)
            message.number = 0
        else:
            message.number = (data[0] << 8) | data[1]

    def encode(self, message):
        return [message.number >> 8, message.number & 0xff]

    def check(self, name, value):
        check_int(value, 0, 0xffff)


class MetaSpec_text(MetaSpec):
    type_byte = 0x01
    attributes = ['text']
    defaults = ['']

    def decode(self, message, data):
        message.text = decode_string(data)

    def encode(self, message):
        return encode_string(message.text)

    def check(self, name, value):
        check_str(value)


class MetaSpec_copyright(MetaSpec_text):
    type_byte = 0x02


class MetaSpec_track_name(MetaSpec_text):
    type_byte = 0x03
    attributes = ['name']
    defaults = ['']

    def decode(self, message, data):
        message.name = decode_string(data)

    def encode(self, message):
        return encode_string(message.name)


class MetaSpec_instrument_name(MetaSpec_track_name):
    type_byte = 0x04


class MetaSpec_lyrics(MetaSpec_text):
    type_byte = 0x05


class MetaSpec_marker(MetaSpec_text):
    type_byte = 0x06


class MetaSpec_cue_marker(MetaSpec_text):
    type_byte = 0x07


class MetaSpec_device_name(MetaSpec_track_name):
    type_byte = 0x09


class MetaSpec_channel_prefix(MetaSpec):
    type_byte = 0x20
    attributes = ['channel']
    defaults = [0]

    def decode(self, message, data):
        message.channel = data[0]

    def encode(self, message):
        return [message.channel]

    def check(self, name, value):
        check_int(value, 0, 0xff)


class MetaSpec_midi_port(MetaSpec):
    type_byte = 0x21
    attributes = ['port']
    defaults = [0]

    def decode(self, message, data):
        if len(data) == 0:
            # Message with length 0 can occur in some files.
            # (See issues 42 and 93.)
            message.port = 0
        else:
            message.port = data[0]

    def encode(self, message):
        return [message.port]

    def check(self, name, value):
        check_int(value, 0, 255)


class MetaSpec_end_of_track(MetaSpec):
    type_byte = 0x2f
    attributes = []
    defaults = []

    def decode(self, message, data):
        pass

    def encode(self, message):
        return []


class MetaSpec_set_tempo(MetaSpec):
    type_byte = 0x51
    attributes = ['tempo']
    defaults = [500000]

    def decode(self, message, data):
        message.tempo = (data[0] << 16) | (data[1] << 8) | (data[2])

    def encode(self, message):
        tempo = message.tempo
        return [tempo >> 16, tempo >> 8 & 0xff, tempo & 0xff]

    def check(self, name, value):
        check_int(value, 0, 0xffffff)


class MetaSpec_smpte_offset(MetaSpec):
    type_byte = 0x54
    attributes = ['frame_rate',
                  'hours',
                  'minutes',
                  'seconds',
                  'frames',
                  'sub_frames'
                  ]
    # TODO: What are some good defaults?
    defaults = [24, 0, 0, 0, 0, 0]

    def decode(self, message, data):
        message.frame_rate = _smpte_framerate_decode[(data[0] >> 6)]
        message.hours = (data[0] & 0x3f)
        message.minutes = data[1]
        message.seconds = data[2]
        message.frames = data[3]
        message.sub_frames = data[4]

    def encode(self, message):
        frame_rate_lookup = _smpte_framerate_encode[message.frame_rate] << 6
        return [frame_rate_lookup | message.hours,
                message.minutes,
                message.seconds,
                message.frames,
                message.sub_frames]

    def check(self, name, value):
        if name == 'frame_rate':
            if value not in _smpte_framerate_encode:
                valid = ', '.join(sorted(_smpte_framerate_encode.keys()))
                raise ValueError('frame_rate must be one of {}'.format(valid))
        elif name == 'hours':
            check_int(value, 0, 255)
        elif name in ['minutes', 'seconds']:
            check_int(value, 0, 59)
        elif name == 'frames':
            check_int(value, 0, 255)
        elif name == 'sub_frames':
            check_int(value, 0, 99)


class MetaSpec_time_signature(MetaSpec):
    type_byte = 0x58
    # TODO: these need more sensible names.
    attributes = ['numerator',
                  'denominator',
                  'clocks_per_click',
                  'notated_32nd_notes_per_beat']
    defaults = [4, 4, 24, 8]

    def decode(self, message, data):
        message.numerator = data[0]
        message.denominator = 2 ** data[1]
        message.clocks_per_click = data[2]
        message.notated_32nd_notes_per_beat = data[3]

    def encode(self, message):
        return [message.numerator,
                int(math.log(message.denominator, 2)),
                message.clocks_per_click,
                message.notated_32nd_notes_per_beat,
                ]

    def check(self, name, value):
        if name == 'denominator':
            # This allows for the ridiculous time signature of
            # 4/57896044618658097711785492504343953926634...
            #   992332820282019728792003956564819968
            check_int(value, 1, 2 ** 255)
            encoded = math.log(value, 2)
            encoded_int = int(encoded)
            if encoded != encoded_int:
                raise ValueError('denominator must be a power of 2')
        else:
            check_int(value, 0, 255)


class MetaSpec_key_signature(MetaSpec):
    type_byte = 0x59
    attributes = ['key']
    defaults = ['C']

    def decode(self, message, data):
        key = signed('byte', data[0])
        mode = data[1]
        try:
            message.key = _key_signature_decode[(key, mode)]
        except KeyError:
            if key < 7:
                msg = ('Could not decode key with {} '
                       'flats and mode {}'.format(abs(key), mode))
            else:
                msg = ('Could not decode key with {} '
                       'sharps and mode {}'.format(key, mode))
            raise KeySignatureError(msg)

    def encode(self, message):
        key, mode = _key_signature_encode[message.key]
        return [unsigned('byte', key), mode]

    def check(self, name, value):
        if value not in _key_signature_encode:
            raise ValueError('invalid key {!r}'.format(value))


class MetaSpec_sequencer_specific(MetaSpec):
    type_byte = 0x7f
    attributes = ['data']
    defaults = [[]]

    def decode(self, message, data):
        message.data = tuple(data)

    def encode(self, message):
        return list(message.data)


def add_meta_spec(klass):
    spec = klass()
    if not hasattr(spec, 'type'):
        name = klass.__name__.replace('MetaSpec_', '')
        spec.type = name

    # This is used by copy().
    spec.settable_attributes = set(spec.attributes) | {'time'}
    _META_SPECS[spec.type_byte] = spec
    _META_SPECS[spec.type] = spec
    _META_SPEC_BY_TYPE[spec.type] = spec


_META_SPECS = {}
_META_SPEC_BY_TYPE = {}


def _add_builtin_meta_specs():
    for name, spec in globals().items():
        if name.startswith('MetaSpec_'):
            add_meta_spec(spec)


_add_builtin_meta_specs()


def build_meta_message(meta_type, data, delta=0):
    # TODO: handle unknown type.
    try:
        spec = _META_SPECS[meta_type]
    except KeyError:
        return UnknownMetaMessage(meta_type, data)
    else:
        msg = MetaMessage(spec.type, time=delta)

        # This adds attributes to msg:
        spec.decode(msg, data)

        return msg


class MetaMessage(BaseMessage):
    is_meta = True

    def __init__(self, type, **kwargs):
        # TODO: handle unknown type?

        spec = _META_SPEC_BY_TYPE[type]
        self_vars = vars(self)
        self_vars['type'] = type

        for name in kwargs:
            if name not in spec.settable_attributes:
                raise ValueError(
                    '{} is not a valid argument for this message type'.format(
                        name))

        for name, value in zip(spec.attributes, spec.defaults):
            self_vars[name] = value
        self_vars['time'] = 0

        for name, value in kwargs.items():
            # Using setattr here because we want type and value checks.
            self._setattr(name, value)

    def copy(self, **overrides):
        """Return a copy of the message

        Attributes will be overridden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.
        """
        if not overrides:
            # Bypass all checks.
            msg = self.__class__.__new__(self.__class__)
            vars(msg).update(vars(self))
            return msg

        if 'type' in overrides and overrides['type'] != self.type:
            raise ValueError('copy must be same message type')

        attrs = vars(self).copy()
        attrs.update(overrides)
        return self.__class__(**attrs)

    # FrozenMetaMessage overrides __setattr__() but we still need to
    # set attributes in __init__().
    def _setattr(self, name, value):
        spec = _META_SPEC_BY_TYPE[self.type]
        self_vars = vars(self)

        if name in spec.settable_attributes:
            if name == 'time':
                check_time(value)
            else:
                spec.check(name, value)
            self_vars[name] = value

        elif name in self_vars:
            raise AttributeError('{} attribute is read only'.format(name))
        else:
            raise AttributeError(
                '{} message has no attribute {}'.format(self.type, name))

    __setattr__ = _setattr

    def bytes(self):
        spec = _META_SPEC_BY_TYPE[self.type]
        data = spec.encode(self)

        return ([0xff, spec.type_byte] +
                encode_variable_int(len(data)) +
                data)

    def __repr__(self):
        spec = _META_SPEC_BY_TYPE[self.type]
        attributes = []
        for name in spec.attributes:
            attributes.append('{}={!r}'.format(name, getattr(self, name)))
        attributes = ' '.join(attributes)
        if attributes:
            attributes = (' {}'.format(attributes))

        return '<meta message {}{} time={}>'.format(self.type,
                                                    attributes, self.time)


class UnknownMetaMessage(MetaMessage):
    def __init__(self, type_byte, data=None, time=0):
        if data is None:
            data = ()
        else:
            data = tuple(data)

        vars(self).update({
            'type': 'unknown_meta',
            'type_byte': type_byte,
            'data': data,
            'time': time})

    def __repr__(self):
        return ('<unknown meta message'
                ' type_byte=0x{:02x} '
                'data={!r} time={}>').format(self.type_byte,
                                             self.data,
                                             self.time
                                             )

    def __setattr__(self, name, value):
        # This doesn't do any checking.
        # It probably should.
        vars(self)[name] = value

    def bytes(self):
        return ([0xff, self.type_byte] +
                encode_variable_int(len(self.data)) +
                list(self.data))
