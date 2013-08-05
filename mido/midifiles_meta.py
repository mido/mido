"""
Meta messages for MIDI files.
"""
from __future__ import print_function, division
import sys
from .messages import BaseMessage

PY2 = (sys.version_info.major == 2)

def encode_signed_byte(byte):
    """Encode integer as two's complement signed byte."""
    if not isinstance(byte, int):
        raise ValueError('argument must be an integer')

    if not -128 <= byte <= 127:
        raise ValueError('signed byte must be in range -128..127')

    if byte < 0:
        # -1 => 255, -2 => 254, ..., -128 => 128
        return 256 + byte
    else:
        return byte


def decode_signed_byte(byte):
    """Convert two's complement signed byte to integer."""
    if not isinstance(byte, int):
        raise ValueError('argument must be an integer')

    if not 0 <= byte <= 255:
        raise ValueError('signed byte must be in range -128..127')

    if byte > 127:
        # 255 => -1, 254 => -2, ..., 128 => -128
        return byte - 256
    else:
        return byte

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


def parse_text(data):
    # Todo: which encoding?
    if PY2:
        convert = unichr
    else:
        convert = chr

    text = ''.join([convert(byte) for byte in data])
    return text


def decode_text(message, data):
    message.value = parse_text(data)


def decode_track_name(message, data):
    message.title = parse_text(data)


def decode_midi_port(message, data):
    # Todo: check if this has to be run through decode_signed_byte
    message.port_number = data[0]


def decode_copyright(message, data):
    message.text = parse_text(data)


def decode_time_signature(message, data):
    # Todo: NEEDS WORK
    # data[0] = numerator of time signature
    # data[1] = denominator of time signature
    # data[2] = number of MIDI clocks in metronome click (erm... yeahhh....)
    # data[3] = "number of notated 32nd notes in a MIDI quarter note"
    
    # message.time_numerator =
    # message.time_denominator =
    # message.clocks_per_click =
    # message. NOT SURE FOR THIS ONE
    message.data = "TIME SIGNATURE MESSAGE, IN DEVELOPMENT"


def decode_key_signature(message, data):
    key, mode = _key_signature_lookup[(decode_signed_byte(data[0]), data[1])]
    message.key = key
    message.mode = mode


def decode_set_tempo(message, data):
    # Tempo is in microseconds per beat.
    message.tempo = (data[0] << 16) | (data[1] << 8) | (data[2])


def decode_text(message, data):
    # Todo: which encoding?

    text = ''.join([chr(byte) for byte in data])
    if PY2:
        text = unicode(text, 'ascii')

    message.text = text


def decode_end_of_track(message, data):
    pass  # No data.


class MetaMessage(BaseMessage):
    _type_name_lookup = {
        # Todo: this needs to be a two_way lookup when we implement
        # saving of files.
        0x01: 'text',
        0x02: 'copyright',
        0x2f: 'end_of_track',
        0x51: 'set_tempo',
        0x03: 'track_name',
        0x58: 'time_signature',
        0x59: 'key_signature',
        0x21: 'midi_port',
        }

    def __init__(self, type_, data=None, **kwargs):
        self.time = 0  # Todo: will this be set by the parser?

        if isinstance(type_, int):
            try:
                self.type = self._type_name_lookup[type_]
            except KeyError:
                print('*** Unknown meta message {:02x}, data={!r}'.format(
                        type_, data))
                self.type = 'meta_unknown_{:02x}'.format(type_)
                self.data = data
            self._data = data

            try:
                decode = globals()['decode_{}'.format(self.type)]
                decode(self, data)
            except LookupError:
                pass  # Ignore unknown type.

        else:
            # This is a copy.
            self.type = type_
            self.__dict__.update(kwargs)

    def _get_values(self):
        values = self.__dict__.copy()
        for key in ['_data', 'type']:
            if key in values:
                del values[key]
        
        return values

    def copy(self, **overrides):
        """Return a copy of the meta message.

        Attributes can be overriden with keyword arguments.
        """
        values = self._get_values()
        values.update(overrides)
        return MetaMessage(self.type, **values)

    def __repr__(self):
        # Todo: this needs to be changed, but don't worry about it for now.
        #return '<meta message type={}, data={!r}, time={}>'.format(
        #    self.type, self._data, self.time)
        values = self._get_values()
        return '{} {!r}'.format(self.type, self._get_values())
