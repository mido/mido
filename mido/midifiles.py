"""
MIDI file reading and playback.

Todo:
    - implement more meta messages
    - make it more fault tolerant (handle errors in MIDI files?)
    - join sysex messages (0xf0...0xf7, 0xf7...0xf7, ...)

References:

http://home.roadrunner.com/~jgglatt/
http://home.roadrunner.com/~jgglatt/tech/miditech.htm
http://home.roadrunner.com/~jgglatt/tech/midifile.htm

http://www.sonicspot.com/guide/midifiles.html
http://www.ccarh.org/courses/253/assignment/midifile/
https://code.google.com/p/binasc/wiki/mainpage
http://stackoverflow.com/questions/2984608/midi-delta-time
http://www.recordingblogs.com/sa/tabid/82/EntryId/44/MIDI-Part-XIII-Delta-time-a
http://www.sonicspot.com/guide/midifiles.html
"""

from __future__ import print_function, division
import os
import io
import sys
import time
from collections import deque, namedtuple
from .messages import BaseMessage, build_message, Message, get_spec

PY2 = (sys.version_info.major == 2)
DEBUG_PARSING = bool(os.environ.get('MIDO_DEBUG_PARSING'))

class ByteReader(object):
    """
    Reads bytes from a binary stream.

    Stream must be a file opened with mode 'rb'.
    """

    # Todo: test if EOFError is raised.

    def __init__(self, stream):
        self.buffer = io.BufferedReader(stream)
        self._pos = 0

    def read_bytearray(self, n):
        """Read n bytes and return as a bytearray."""
        self._pos += n
        return bytearray(self.buffer.read(n))

    def read_byte_list(self, n):
        """Read n bytes and return as a list."""
        return list(self.read_bytearray(n))

    def read_byte(self):
        """Read one byte."""
        byte = self.read_byte_list(1)[0]
        if DEBUG_PARSING:
            print('  {:04x}: {:02x}'.format(self.tell(), byte))
        return byte

    def peek_byte(self):
        """Return the next byte in the file.

        This can be used for look-ahead."""
        # Todo: this seems a bit excessive for just one byte.
        byte = bytearray(self.buffer.peek(1))[0]
        if DEBUG_PARSING:
            print('  Peek: {:04x}: {:02x}'.format(self.tell(), byte))
        return byte

    def read_short(self):
        """Read short (2 bytes little endian)."""
        a, b = self.read_byte_list(2)
        return a << 8 | b

    def read_long(self):
        """Read long (4 bytes little endian)."""
        a, b, c, d = self.read_byte_list(4)
        return a << 24 | b << 16 | c << 8 | d

    def tell(self):
        return self._pos

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False


def encode_signed_byte(byte):
    """Encode integer as two's complement signed byte."""
    if not isinstance(byte, int):
        raise ValueError('argument must be an integer')

    if not -128 <= byte <= 127:
        raise ValueError('signed byte must be in range -128..127')

    if byte < 0:
        #
        # -1 => 255
        # -2 => 254
        # ...
        # -128 => 128
        # 
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
        #
        # 255 => -1
        # 254 => -2
        # ...
        # 128 => -128
        # 
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


class Track(list):
    """
    The 'name' property will set and get the track name using a
    MetaMessage of type 'track_name'. Get returns the first
    'track_name' in the track (and ignores the rest). Set modifies the
    first 'track_name', or if one is not found, adds one to the
    beginning of the track with delta time 0.
    """

    def __init__(self):
        list.__init__([])

    def _get_name(self):
        for message in self:
            if message.type == 'track_name':
                return message.title
        else:
            return u''

    def _set_name(self, name):
        # Find the first track_name message and modify it.
        for message in self:
            if message.type == 'track_name':
                message.title = name
                return
        else:
            # No track name found, add one.
            self.insert(0, MetaMessage('track_name', title=name, time=0))

    name = property(fget=_get_name, fset=_set_name)
    del _get_name, _set_name


class MidiFile:
    def __init__(self, filename):
        self.filename = filename
        self.tracks = []

        with ByteReader(open(filename, 'rb')) as self.file:
            # Read header (16 bytes)
            magic = self.file.read_bytearray(4)
            if not magic == bytearray(b'MThd'):
                # Todo: raise some other error?
                raise IOError('not a MIDI file')

            header_size = self.file.read_long()

            self.format = self.file.read_short()
            number_of_tracks = self.file.read_short()
            self.ticks_per_quarter_note = self.file.read_short()

            for i in range(number_of_tracks):
                self.tracks.append(self._read_track())
                # Todo: used to ignore EOFError. I hope things still work.
        
    def _print_tracks(self):
        for i, track in enumerate(self.tracks):
            sys.stdout.write('=== Track {}\n'.format(i))
            for event in track:
                sys.stdout.write('  {!r}\n'.format(event))

    def _get_info(self):
        for i, track in enumerate(self.tracks):
            sys.stdout.write('=== Track {}\n'.format(i))
            for event in track:
                sys.stdout.write('  {!r}\n'.format(event))

    def _read_delta_time(self):
        delta = 0

        while 1:
            byte = self.file.read_byte()
            delta = (delta << 7) | (byte & 0x7f)
            if not byte & 0x80:
                break
        
        return delta

    def _read_message(self, status_byte):
        bytes = [status_byte]
        spec = get_spec(status_byte)

        for i in range(spec.length - 1):
            bytes.append(self.file.read_byte())

        # Value > 127 occurs sometimes.
        # Clip it so it's inside valid range.
        # (This is what timidity does.)
        # if spec.type == 'control_change':
        #     if bytes[-1] > 127:
        #         bytes[-1] = 127
        # elif spec.type in ['note_on', 'note_off']:
        #     for i in [1, 2]:
        #         bytes[i] &= 0x7f

        return build_message(bytes)

    def _read_meta_message(self):
        type = self.file.read_byte()
        length = self.file.read_byte()
        data = self.file.read_byte_list(length)

        return MetaMessage(type, data)

    def _read_sysex(self):
        length = self.file.read_byte()
        data = self.file.read_byte_list(length)

        if data and data[-1] == 0xf7:
            data = data[:-1]

        message = Message('sysex', data=data)
        return message

    def _read_track(self):
        track = Track()

        magic = self.file.read_bytearray(4)
        if magic != bytearray(b'MTrk'):
            raise IOError("track doesn't start with 'MTrk'")

        length = self.file.read_long()  # Ignore this.
        start = self.file.tell()
        last_status = None

        while 1:
            # End of track reached.
            if self.file.tell() - start == length:
                break

            if DEBUG_PARSING:
                print('delta:')
            delta = self._read_delta_time()

            if DEBUG_PARSING:
                print('message:')

            peek_status = self.file.peek_byte()

            # Todo: not all messages have running status
            if peek_status < 0x80:
                if last_status is None:
                    # Todo: add file offset to error message?
                    raise IOError('running status when last_status is None!')
                status_byte = last_status
            else:
                status_byte = self.file.read_byte()
                last_status = status_byte

            if status_byte == 0xff:
                message = self._read_meta_message()
            elif status_byte == 0xf0:
                message = self._read_sysex()
            elif status_byte == 0xf7:
                # Todo: handle continuation of previous sysex
                message = self._read_sysex()
            else:
                message = self._read_message(status_byte)

            message.time = delta

            if DEBUG_PARSING:
                print('    =>', message)
            track.append(message)

            if message.type == 'end_of_track':
                break

        return track

    def play(self, yield_meta_messages=False):
        """Play back all tracks.

        Yields all messages in all tracks in temporal order, with
        correct timing. (It pauses with time.sleep() between each
        message according to delta times and current tempo.)

        Each message returned will be a copy of the one in the
        track, so you can safely modify it without ruining the
        tracks. The time attribute will be set to 0.
        """

        # The tracks of format 2 files are not in sync, so they can
        # not be played back like this.
        if self.format == 2:
            raise ValueError('format 2 file can not be played back like this')

        # Make a copy of the tracks, since we'll be removing from them.
        tracks = [deque(track) for track in self.tracks]
        messages_left = sum(map(len, tracks))

        def compute_seconds_per_tick(tempo):
            """Compute seconds per tick."""
            seconds_per_quarter_note = (tempo / 1000000.0)
            return seconds_per_quarter_note / self.ticks_per_quarter_note

        # The default tempo is 120 BPM.
        # (500000 microseconds per quarter note.)
        seconds_per_tick = compute_seconds_per_tick(500000)

        # Convert time of all message to absolute time (in ticks)
        # so they can be sorted
        messages = []
        for i, track in enumerate(self.tracks):
            now = 0
            for message in track:
                if message.type == 'end_of_track':
                    break
                now += message.time
                messages.append(message.copy(time=now))

        messages.sort(key=lambda x: x.time)

        now = 0
        for message in messages:
            delta = message.time - now
            if delta:
                sleep_time = delta * seconds_per_tick
                time.sleep(sleep_time)
            if isinstance(message, Message):
                yield message.copy()
            now += delta

            if message.type == 'set_tempo':
                seconds_per_tick = compute_seconds_per_tick(message.tempo)

    def __iter__(self):
        for message in self.play():
            yield message

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False
