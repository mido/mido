"""
Meta messages for MIDI files.

Todo:
     - what if an unknown meta message is implemented and someone depends on
       the 'data' attribute?
     - is 'type_byte' a good name?
     - 'values' is not a good name for a dictionary.
     - type and value safety?
     - copy().
     - expose _key_signature_encode/decode?
"""
from __future__ import print_function, division
import sys
import math
import struct
from contextlib import contextmanager
from ..messages import BaseMessage, check_time

PY2 = (sys.version_info.major == 2)

_charset = 'latin1'

def reverse_table(table):
    """Return value: key for dictionary."""
    return {value: key for (key, value) in table.items()}

_key_signature_decode = {
        (-7, 0): 'Cb',
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
_key_signature_encode = reverse_table(_key_signature_decode)

_smpte_framerate_decode = {
        0: 24,
        1: 25,
        2: 29.97,
        3: 30,
    }
_smpte_framerate_encode = reverse_table(_smpte_framerate_decode)

def signed(to_type, n):
    formats = {
        'byte': 'Bb',
        'short': 'Hh',
        'long': 'Ll',
        'ubyte': 'bB',
        'ushort': 'hH',
        'ulong': 'lL',
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
    if not isinstance(value, int) or value < 0:
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

def bpm2tempo(bpm):
    """Convert beats per minute to MIDI file tempo.

    Returns microseconds per beat as an integer::
    
        240 => 250000
        120 => 500000
        60 => 1000000
    """
    # One minute is 60 million microseconds.
    return int(round((60 * 1000000) / bpm))

def tempo2bpm(tempo):
    """Convert MIDI file tempo to BPM.

    Returns BPM as an integer or float::

        250000 => 240
        500000 => 120
        1000000 => 60
    """
    # One minute is 60 million microseconds.
    return (60 * 1000000) / tempo

@contextmanager
def meta_charset(tmp_charset):
    global _charset
    old = _charset
    _charset = tmp_charset
    yield
    _charset = old

def check_int(value, low, high):
    if not isinstance(value, int):
        raise TypeError('attribute must be an integer')
    elif not low <= value <= high:
        raise ValueError('attribute must be in range {}..{}'.format(low, high))

if PY2:
    def check_str(value):
        if not isinstance(value, basestring):
            raise TypeError('attribute must be unicode or string')
else:
    def check_str(value):
        if not isinstance(value, str):
            raise TypeError('attribute must a string')

class MetaSpec(object):
    def check(self, name, value):
        pass

class MetaSpec_sequence_number(MetaSpec):
    type_byte = 0x00
    attributes = ['number']
    defaults = [0]

    def decode(self, message, data):
        message.number = (data[0] << 8) | data[1]

    def encode(self, message):
        return [message.number >> 8, message.number & 0xff]

    def check(self, name, value):
        check_int(value, 0, 255)
            
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
    # Todo: What are some good defaults?
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
    # Todo: these need more sensible names.
    attributes = ['numerator',
                  'denominator',
                  'clocks_per_click',
                  'notated_32nd_notes_per_beat']
    defaults = [4, 2, 24, 8]

    def decode(self, message, data):
        message.numerator = data[0]
        message.denominator = 2 ** data[1]
        message.clocks_per_click = data[2]
        message.notated_32nd_notes_per_beat = data[3]

    def encode(self, message):
        return [
            message.numerator,
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
        message.key = _key_signature_decode[(key, mode)]

    def encode(self, message):
        key, mode = _key_signature_encode[message.key]
        return [unsigned('byte', key), mode]

    def check(self, name, value):
        if not value in _key_signature_encode:
            raise ValueError('invalid key {!r}'.format(value))

class MetaSpec_sequencer_specific(MetaSpec):
    type_byte = 0x7f
    attributes = ['data']
    defaults = [[]]

    def decode(self, message, data):
        message.data = tuple(data)

    def encode(self, message):
        return list(message.data)

_specs = {}

def add_meta_spec(klass):
    spec = klass()
    if not hasattr(spec, 'type'):
        name = klass.__name__.replace('MetaSpec_', '')
        spec.type = name
    # This is used by copy().
    spec.settable_attributes = set(spec.attributes) | {'time'}
    _specs[spec.type_byte] = spec
    _specs[spec.type] = spec
    
def _add_builtin_meta_specs():
    for name in globals():
        if name.startswith('MetaSpec_'):
            add_meta_spec(globals()[name])

_add_builtin_meta_specs()


def build_meta_message(type_, data, delta=0):
    # Todo: handle unknown type.
    try:
        spec = _specs[type_]
    except KeyError:
        return UnknownMetaMessage(type_, data)

    message = MetaMessage(spec, time=delta)
    spec.decode(message, data)
    return message

class MetaMessage(BaseMessage):
    def __init__(self, type_, **kwargs):
        # Todo: allow type_ to be a type byte?
        # Todo: handle unknown type.
        if isinstance(type_, MetaSpec):
            vars(self)['_spec'] = type_
        else:
            vars(self)['_spec'] = _specs[type_]

        vars(self)['type'] = self._spec.type

        for name in kwargs:
            if name == 'time':
                continue  # Time is always allowed.

            if name not in self._spec.settable_attributes:
                raise ValueError(
                    '{} is not a valid argument for this message type'.format(
                        name))

        for name, value in zip(self._spec.attributes, self._spec.defaults):
            vars(self)[name] = value
        vars(self)['time'] = 0

        for name, value in kwargs.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if name in self._spec.settable_attributes:
            if name == 'time':
                check_time(value)
            else:
                self._spec.check(name, value)
            vars(self)[name] = value
        elif name in vars(self):
            raise AttributeError('{} attribute is read only'.format(name))
        else:
            raise AttributeError(
                '{} message has no attribute {}'.format(self.type, name))

    def bytes(self):
        data = self._spec.encode(self)
        return ([0xff, self._spec.type_byte]
                + encode_variable_int(len(data))
                + data)
    
    def __repr__(self):
        attributes = []
        for name in self._spec.attributes:
            attributes.append('{}={!r}'.format(name, getattr(self, name)))
        attributes = ' '.join(attributes)
        if attributes:
            attributes = (' {}'.format(attributes))

        return '<meta message {}{} time={}>'.format(self.type,
                                                    attributes, self.time)

class UnknownMetaMessage(MetaMessage):
    def __init__(self, type_byte, data=None, time=0):
        if data is None:
            data = []

        self.type = 'unknown_meta'
        self._type_byte = type_byte
        self._data = data
        self.time = time

    def __repr__(self):
        return ('<unknown meta message'
                ' _type_byte=0x{:02x} _data={!r} time={}>').format(
                self._type_byte,
                self._data,
                self.time)

    # Override all checking.
    def __setattr__(self, name, value):
        vars(self)[name] = value

    def bytes(self):
        return ([0xff, self._type_byte]
                + encode_variable_int(len(self._data))
                + self._data)
