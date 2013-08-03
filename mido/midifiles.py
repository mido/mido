"""
An incomplete MIDI file reader.

Reads most MIDI files, but fails with others.

Todo:
    - return MetaMessages along with Messages?
    - join sysex messages (0xf0...0xf7, 0xf7...0xf7, ...)
    - handle the too short files listed below:

    mid2/Portsmouth.mid
    mid1/acso3op2.mid

References:

http://www.sonicspot.com/guide/midifiles.html
http://www.ccarh.org/courses/253/assignment/midifile/
https://code.google.com/p/binasc/wiki/mainpage
http://stackoverflow.com/questions/2984608/midi-delta-time
http://www.recordingblogs.com/sa/tabid/82/EntryId/44/MIDI-Part-XIII-Delta-time-a
http://www.sonicspot.com/guide/midifiles.html
"""

from __future__ import print_function
import sys
import time
from collections import deque, namedtuple
from .messages import BaseMessage, build_message, Message, get_spec

PY2 = (sys.version_info.major == 2)

class ByteReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.data = deque()

        for line in stream:
            self.data.extend(bytearray(line))

        self._pos = 0

    def read_bytes(self, n):
        return [self.read_byte() for _ in range(n)]

    def read_bytearray(self, n):
        return bytearray(self.read_bytes(n))

    def read_byte(self):
        """Get the next byte from."""
        try:
            byte = self.data.popleft()
            # print('  {:04x}: {:02x}'.format(self.tell(), byte))
            self._pos += 1
            return byte
        except IndexError:
            raise EOFError('end of file reached')

    def unread_byte(self, byte):
        """Put a byte back.

        This can be used for look-ahead."""
        self.data.appendleft(byte)
        self._pos -= 1

    def tell(self):
        return self._pos

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

    def __iter__(self):
        while 1:
            yield self.data.popleft()


class FileReader(ByteReader):
    def read_short(self):
        a, b = [self.read_byte() for i in range(2)]
        return a << 8 | b

    def read_long(self):
        a, b, c, d = [self.read_byte() for i in range(4)]
        return a << 24 | b << 16 | c << 8 | d


class EndOfTrack(IOError):
    pass


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


def decode_set_tempo(message, data):
    # Tempo is in microseconds per beat.
    # Convert big endian 3 bytes with 7 bit bytes into
    # and integer.
    message.tempo = data[0] | data[1] << 7 | data[2] << 14


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
        0x01 : 'text',
        0x2f : 'end_of_track',
        0x51 : 'set_tempo', 
        }

    def __init__(self, type_, data=None, **kwargs):
        self.time = 0  # Todo: will this be set by the parser?

        if isinstance(type_, int):
            try:
                self.type = self._type_name_lookup[type_]
            except KeyError:
                # print('  *** Unknown meta message type 0x{:02x}'.format(
                #         type_))
                self.type = None  # Todo: we just ignore this for now
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


class MidiFile:
    def __init__(self, filename):
        self.filename = filename
        self.tracks = []
        self._current_track = []
        self._running_status = None

        with FileReader(open(filename, 'rb')) as self.file:
            # Read header (16 bytes)
            magic = self.file.read_bytearray(4)
            if not magic == bytearray(b'MThd'):
                # Todo: raise some other error?
                raise ValueError('not a MIDI file')

            header_size = self.file.read_long()

            self.file_format = self.file.read_short()
            self.number_of_tracks = self.file.read_short()
            self.ticks_per_quarter_note = self.file.read_short()

            self._read_tracks()
        
    def _print_tracks(self):
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

    def _read_meta_event(self):
        type = self.file.read_byte()
        length = self.file.read_byte()
        data = self.file.read_bytes(length)

        return MetaMessage(type, data)

    def _read_message(self, status_byte):
        # Todo: not all messages have running status
        if status_byte < 0x80:
            if self._running_status is None:
                return
            status_byte = self._running_status
            # self.file.unread_byte(status_byte)
        else:
            self._running_status = status_byte

        try:
            spec = get_spec(status_byte)
        except LookupError:
            sys.exit(1)

        bytes = [status_byte]

        for i in range(spec.length - 1):
            bytes.append(self.file.read_byte())

        message = build_message(bytes)

        return message


    def _read_sysex(self):
        length = self.file.read_byte()
        data = self.file.read_bytes(length)
        if data[-1] == 0xf7:
            data = data[:-1]

        message = Message('sysex', data=data)

        return message


    def _read_event(self, delta):
        status_byte = self.file.read_byte()
        if status_byte >= 0x80:
            self._running_status = status_byte
        else:
            self.file.unread_byte(status_byte)
            status_byte = self._running_status

        if status_byte == 0xff:
            event = self._read_meta_event()

        elif status_byte == 0xf0:
            event = self._read_sysex()

        elif status_byte == 0xf7:
            event = self._read_sysex()  # Todo: continuation of previous sysex

        else:
            event = self._read_message(status_byte)

        if event is not None:
            event.time = delta
            # print('    =>', event)
            self._current_track.append(event)
            if event.type == 'end_of_track':
                raise EndOfTrack()

    def _read_track(self):
        magic = self.file.read_bytearray(4)
        if magic != bytearray(b'MTrk'):
            raise ValueError("track doesn't start with 'MTrk'")

        length = self.file.read_long()  # Ignore this.

        self._current_track = []
        self._running_status = None

        start = self.file.tell()

        while 1:
            try:
                # End of track reached
                if self.file.tell() - start == length:
                    break

                # print('delta:')
                delta = self._read_delta_time()
                # print('message:')
                self._read_event(delta)
            except EndOfTrack:
                break

        self.tracks.append(self._current_track)
        self._current_track = []

    def _read_tracks(self):
        try:
            for i in range(self.number_of_tracks):
                self._read_track()
        except EOFError:
            pass

    def play(self, yield_meta_messages=False, tempo_scale=1.0):
        """Play back all tracks.

        Yields all messages in all tracks in temporal order, with
        correct timing. (It pauses with time.sleep() between each
        message according to delta times and current tempo.)

        Each message returned will be a copy of the one in the
        track, so you can safely modify it without ruining the
        tracks. The time attribute will be set to 0.
        """

        # Todo: delta time is not converted correctly.
        # The unit is MIDI ticks, whose duration depend on time signature.
        # This is a little too complex for the first implementation.
        
        # Make a copy of the tracks, since we'll be removing from them.
        tracks = [deque(track) for track in self.tracks]
        messages_left = sum(map(len, tracks))

        # The default tempo is 120 BPM.
        tempo = 500000  # Microseconds per beat.
        # tempo = 5000000 / 1.5
        tempo /= tempo_scale

        elapsed = 0

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
                sleep_time = (tempo * delta) / 1000000000.0
                time.sleep(sleep_time)
            if isinstance(message, Message):
                yield message.copy()
            now += delta

            # Todo: set tempo before or after?
            # if message.type == 'set_tempo':
            #     tempo = message.tempo

    def __iter__(self):
        for message in self.play():
            yield message

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False


# mid1/acso3op2.mid:
# 00008b0: 00c0 0604 b05b 5400 5d5d 8168 0a58 0307
#          (prog )(control )(? ... )(note off)(? )
#
# 00008c0: 7f81 4a90 4057 0043 5901 4854 1940 0001
#          (off ?  ) (?                          )
