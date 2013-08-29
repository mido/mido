"""
Meta messages for MIDI files.

Todo:
     - what if an unknown meta message is implemented and someone depends on
       the 'data' attribute?
     - is 'type_byte' a good name?
     - 'values' is not a good name for a dictionary.
     - type and value safety?
     - copy().
     - expose _key_signature_lookup?
"""
from __future__ import print_function, division
import sys
from .messages import BaseMessage
from .types import signed, unsigned

PY2 = (sys.version_info.major == 2)

_charset = 'latin1'

def reverse_table(table):
    """Return value: key for dictionary."""
    return {value: key for (key, value) in table.items()}

_key_signature_lookup = {
        (-7, 0): ('Cb', 'major'),
        (-6, 0): ('Gb', 'major'),
        (-5, 0): ('Db', 'major'),
        (-4, 0): ('Ab', 'major'),
        (-3, 0): ('Eb', 'major'),
        (-2, 0): ('Bb', 'major'),
        (-1, 0): ('F', 'major'),
        (0, 0): ('C', 'major'),
        (1, 0): ('G', 'major'),
        (2, 0): ('D', 'major'),
        (3, 0): ('A', 'major'),
        (4, 0): ('E', 'major'),
        (5, 0): ('B', 'major'),
        (6, 0): ('F#', 'major'),
        (7, 0): ('C#', 'major'),
        (-7, 1): ('Ab', 'minor'),
        (-6, 1): ('Eb', 'minor'),
        (-5, 1): ('Bb', 'minor'),
        (-4, 1): ('F', 'minor'),
        (-3, 1): ('C', 'minor'),
        (-2, 1): ('G', 'minor'),
        (-1, 1): ('D', 'minor'),
        (0, 1): ('A', 'minor'),
        (1, 1): ('E', 'minor'),
        (2, 1): ('B', 'minor'),
        (3, 1): ('F#', 'minor'),
        (4, 1): ('C#', 'minor'),
        (5, 1): ('G#', 'minor'),
        (6, 1): ('D#', 'minor'),
        (7, 1): ('A#', 'minor'),
    }
_key_signature_lookup.update(reverse_table(_key_signature_lookup))

_smpte_framerate_lookup = {
        0: 24,
        1: 25,
        2: 29.97,
        3: 30,
    }
_smpte_framerate_lookup.update(reverse_table(_smpte_framerate_lookup))

def decode_text(data):
    return bytearray(data).decode(_charset)

def encode_text(text):
    return list(bytearray(text.encode(_charset)))

class MetaSpec(object):
    pass

class MetaSpec_sequence_number(MetaSpec):
    type_byte = 0x00
    attributes = ['number']
    defaults = [0]

    def decode(self, message, data):
        message.number = (data[0] << 8) | data[1]

    def encode(self, message):
        return [message.number >> 8, message.number & 0xff]

class MetaSpec_text(MetaSpec):
    type_byte = 0x01
    attributes = ['text']
    defaults = ['']

    def decode(self, message, data):
        message.text = decode_text(data)

    def encode(self, message):
        return encode_text(message.text)

class MetaSpec_copyright(MetaSpec_text):
    type_byte = 0x02

class MetaSpec_track_name(MetaSpec):
    type_byte = 0x03
    attributes = ['name']
    defaults = ['']
    
    def decode(self, message, data):
        message.name = decode_text(data)

    def encode(self, message):
        return encode_text(message.name)

class MetaSpec_instrument_name(MetaSpec):
    type_byte = 0x04
    attributes = ['name']
    defaults = ['']

    def decode(self, message, data):
        message.name = decode_text(data)

    def encode(self, message):
        return encode_text(message.name)

class MetaSpec_lyrics(MetaSpec_text):
    type_byte = 0x05

class MetaSpec_marker(MetaSpec_text):
    type_byte = 0x06

class MetaSpec_cue_marker(MetaSpec_text):
    type_byte = 0x07

class MetaSpec_midi_port(MetaSpec):
    type_byte = 0x21
    attributes = ['port']
    defaults = [0]

    def decode(self, message, data):
        message.port = data[0]

    def encode(self, message):
        return [message.port]

class MetaSpec_channel_prefix(MetaSpec):
    type_byte = 0x20
    attributes = ['channel']
    defaults = [0]

    def decode(self, message, data):
        message.channel = data[0]

    def encode(self, message):
        return [message.channel]

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
        message.frame_rate = _smpte_framerate_lookup[(data[0] >> 6)]
        message.hours = (data[0] & 0x3f)
        message.minutes = data[1]
        message.seconds = data[2]
        message.frames = data[3]
        message.sub_frames = data[4]

    def encode(self, message):
        frame_rate_lookup = _smpte_framerate_lookup[message.frame_rate] << 6
        return [frame_rate_lookup | message.hours,
                message.minutes,
                message.seconds,
                message.frames,
                message.sub_frames]

class MetaSpec_time_signature(MetaSpec):
    type_byte = 0x58
    # Todo: these need more sensible names.
    # Todo: use 
    attributes = ['numerator',
                  'denominator',
                  'clocks_per_click',
                  'notatated_32nd_notes_per_beat']
    # Todo: find good defaults here.
    defaults = [4, 4, 0, 0]

    def decode(self, message, data):
        for name, value in zip(self.attributes, data):
            setattr(message, name, value)

    def encode(self, message):
        data = []
        for name in self.attributes:
            data.append(getattr(message, name))
        return data

class MetaSpec_key_signature(MetaSpec):
    type_byte = 0x59
    attributes = ['key', 'mode']
    defaults = ['C', 'major']

    def decode(self, message, data):
        key = signed('byte', data[0])
        mode = data[1]
        message.key, message.mode = _key_signature_lookup[(key, mode)]

    def encode(self, message):
        key, mode = _key_signature_lookup[message.key, message.mode]
        return [unsigned('byte', key), mode]

class MetaSpec_sequencer_specific(MetaSpec):
    type_byte = 0x7f
    attributes = ['data']
    defaults = [[]]

    def decode(self, message, data):
        message.data = data

    def encode(self, message):
        return message.data

_specs = {}

# Todo: rethink this before launch.
#       Should this take an object or a class?
def add_meta_spec(klass):
    spec = klass()
    if not hasattr(spec, 'type'):
        name = klass.__name__.replace('MetaSpec_', '')
        spec.type = name
    _specs[spec.type_byte] = spec
    _specs[spec.type] = spec
    
def _add_builtin_meta_specs():
    for name in globals():
        if name.startswith('MetaSpec_'):
            add_meta_spec(globals()[name])

_add_builtin_meta_specs()


def _build_meta_message(type_, data):
    # Todo: handle unknown type.
    try:
        spec = _specs[type_]
    except KeyError:
        return UnknownMetaMessage(type_, data)

    message = MetaMessage(spec)
    spec.decode(message, data)
    return message

class MetaMessage(BaseMessage):
    def __init__(self, type_, **kwargs):
        # Todo: allow type_ to be a type byte?
        # Todo: handle unknown type.
        if isinstance(type_, MetaSpec):
            self._spec = type_
        else:
            self._spec = _specs[type_]

        self.type = self._spec.type

        for name in kwargs:
            if name == 'time':
                continue  # Time is always allowed.

            if name not in self._spec.attributes:
                raise ValueError(
                    '{} is not a valid argument for this message type'.format(
                        name))

        for name, value in zip(self._spec.attributes, self._spec.defaults):
            setattr(self, name, value)
        self.time = 0

        self.__dict__.update(kwargs)

    def copy(self, **overrides):
        # Todo: check attribute names (and types and values).
        klass = self.__class__
        message = klass.__new__(klass)
        message.__dict__.update(self.__dict__)
        message.__dict__.update(overrides)
        return message

    def bytes(self):
        data = self._spec.encode(self)
        return [0xff, self._spec.type_byte, len(data)] + data
    
    def __repr__(self):
        attributes = []
        for name in self._spec.attributes:
            attributes.append('{}={!r}'.format(name, getattr(self, name)))
        attributes = ', '.join(attributes)
        if attributes:
            attributes = (' {}'.format(attributes))

        return '<meta message {}{} time={}>'.format(self.type,
                                                    attributes, self.time)

# Todo: what if one of these messages is implemented?
class UnknownMetaMessage(MetaMessage):
    def __init__(self, type_byte, data=None, time=0):
        if data is None:
            data = []

        self.type = 'unknown_meta'
        self._type_byte = type_byte
        self._data = data
        self.time = time

    def __repr__(self):
        return '<unknown meta message 0x{:02x} _data={!r}, time={}>'.format(
            self._type_byte,
            self._data,
            self.time)

    def bytes(self):
        return [0xff, self._type_byte, len(self._data)] + self._data
