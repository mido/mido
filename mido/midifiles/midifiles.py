"""
MIDI file reading and playback.

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
import io
import sys
import time
import string
import struct
from ..messages import build_message, Message, get_spec
from .meta import MetaMessage, _build_meta_message, meta_charset
from .meta import MetaSpec, add_meta_spec, encode_variable_int

PY2 = (sys.version_info.major == 2)

# The default tempo is 120 BPM.
# (500000 microseconds per beat (quarter note).)
DEFAULT_TEMPO = 500000
DEFAULT_TICKS_PER_BEAT = 480

class ByteReader(object):
    """
    Reads bytes from a file.
    """
    def __init__(self, file):
        """
        :param file:  a file object which is opened in read mode,
                      typically a file or an in-memory file.
        """
        self._buffer = list(bytearray(file.read()))
        self.pos = 0
        self._eof = EOFError('unexpected end of file')

    def read_byte(self):
        """Read one byte."""
        try:
            byte = self._buffer[self.pos]
            self.pos += 1
            return byte
        except IndexError:
            raise self._eof

    def peek_byte(self):
        """Return the next byte in the file.

        This can be used for look-ahead."""
        try:
            return self._buffer[self.pos]
        except IndexError:
            raise self._eof

    def peek_list(self, n):
        """Return a list of the next n bytes."""
        return self._buffer[self.pos:self.pos+n]

    def read_short(self):
        """Read short (2 bytes little endian)."""
        a, b = self.read_list(2)
        return a << 8 | b

    def read_long(self):
        """Read long (4 bytes little endian)."""
        a, b, c, d = self.read_list(4)
        return a << 24 | b << 16 | c << 8 | d

    def read_list(self, n):
        """Read n bytes and return as a list."""
        i = self.pos
        ret = self._buffer[i:i + n]
        if len(ret) < n:
            raise self._eof

        self.pos += n
        return ret


class _DebugByteReader(ByteReader):
    parent = ByteReader

    def _print_bytes(self, n):
        """Print the next n bytes as hex and characters.

        This is used for debugging.
        """
        data = self._buffer[self.pos:self.pos + n]
        # print()
        for pos, byte in enumerate(data, start=self.pos):
            char = chr(byte)
            if not char in string.printable or char in string.whitespace:
                char = '.'
            print('  {:06x}: {:02x}  {}'.format(pos, byte, char))

        if len(data) < n:
            raise EOFError('unexpected end of file')

    def read_byte(self):
        self._print_bytes(1)
        return self.parent.read_byte(self)

    def read_list(self, n):
        self._print_bytes(n)
        return self.parent.read_list(self, n)


class MidiTrack(list):
    @property
    def name(self):
        """Name of the track.

        This will return the name from the first track_name meta
        message in the track, or '' if there is no such message.

        Setting this property will update the name field of the first
        track_name message in the track. If no such message is found,
        one will be added to the beginning of the track with a delta
        time of 0."""
        for message in self:
            if message.type == 'track_name':
                return message.name
        else:
            return u''

    @name.setter
    def name(self, name):
        # Find the first track_name message and modify it.
        for message in self:
            if message.type == 'track_name':
                message.name = name
                return
        else:
            # No track name found, add one.
            self.insert(0, MetaMessage('track_name', name=name, time=0))

    def copy(self):
        return self.__class__(self)

    def __getitem__(self, index_or_slice):
        # Retrieve item from the MidiTrack
        lst = list.__getitem__(self, index_or_slice)
        if isinstance(index_or_slice, int):
            # If an index was provided, return the list element
            return lst
        else:
            # Otherwise, construct a MidiTrack to return.
            # Todo: this make a copy of the list. Is there a better way?
            return self.__class__(lst)

    def __add__(self, other):
        return self.__class__(list.__add__(self, other))

    def __mul__(self, other):
        return self.__class__(list.__mul__(self, other))

    def __repr__(self):
        return '<midi track {!r} {} messages>'.format(self.name, len(self))


def _dbg(text=''):
    print(text)


def _write_chunk(outfile, name, data):
    """Write an IFF chunk to the file.

    `name` must be a bytestring."""
    outfile.write(name)
    outfile.write(struct.pack('>L', len(data)))
    outfile.write(data)


class MidiFile:
    def __init__(self, filename=None, file=None,
                 type=1, ticks_per_beat=DEFAULT_TICKS_PER_BEAT,
                 charset='latin1',
                 debug=False):

        self.filename = filename
        self.type = type
        self.ticks_per_beat = ticks_per_beat
        self.charset = charset
        self.debug = debug

        self.tracks = []

        if type not in range(3):
            raise ValueError(
                'invalid format {} (must be 0, 1 or 2)'.format(format))

        if file is not None:
            self._load(file)
        elif self.filename is not None:
            with io.open(filename, 'rb') as file:
                self._load(file)

    def add_track(self, name=None):
        """Add a new track to the file.

        This will create a new MidiTrack object and append it to the
        track list.
        """
        track = MidiTrack()
        if name is not None:
            track.name = name
        self.tracks.append(track)
        return track

    def _load(self, file):
        if self.debug:
            self._file = _DebugByteReader(file)
        else:
            self._file = ByteReader(file)

        with meta_charset(self.charset):
            if self.debug:
                _dbg('Header:')

            # Read header (16 bytes)
            magic = self._file.peek_list(4)
            if not bytearray(magic) == bytearray(b'MThd'):
                raise IOError('MThd not found. Probably not a MIDI file')
            self._file.read_list(4)  # Skip MThd

            # This is always 6 for any file created under the MIDI 1.0
            # specification, but this allows for future expansion.
            header_size = self._file.read_long()

            self.type = self._file.read_short()
            number_of_tracks = self._file.read_short()
            self.ticks_per_beat = self._file.read_short()

            if self.debug:
                _dbg('-> type={}, tracks={}, ticks_per_beat={}'.format(
                    self.type, number_of_tracks, self.ticks_per_beat))
                _dbg()

            # Skip the rest of the header.
            for _ in range(header_size - 6):
                self._file.read_byte()

            for i in range(number_of_tracks):
                self.tracks.append(self._read_track())
                # Todo: used to ignore EOFError. I hope things still work.

    def _read_variable_int(self):
        delta = 0

        while True:
            byte = self._file.read_byte()
            delta = (delta << 7) | (byte & 0x7f)
            if byte < 0x80:
                return delta

    def _read_message(self, status_byte):
        try:
            spec = get_spec(status_byte)
        except LookupError:
            raise IOError('undefined status byte 0x{:02x}'.format(status_byte))
        data_bytes = self._file.read_list(spec.length - 1)
        for byte in data_bytes:
            if byte > 127:
                raise IOError('data byte must be in range 0..127')
        return build_message(spec, [status_byte] + data_bytes)

    def _read_meta_message(self):
        type = self._file.read_byte()
        length = self._read_variable_int()
        data = self._file.read_list(length)
        return _build_meta_message(type, data)

    def _read_sysex(self):
        length = self._read_variable_int()
        data = self._file.read_list(length)

        # Strip start and end bytes.
        if data and data[0] == 0xf0:
            data = data[1:]
        if data and data[-1] == 0xf7:
            data = data[:-1]

        message = Message('sysex', data=data)
        return message

    def _read_track(self):
        track = MidiTrack()

        if self.debug:
            _dbg('Track {}:'.format(len(self.tracks)))

        magic = self._file.peek_list(4)
        if bytearray(magic) == bytearray(b'MTrk'):
            self._file.read_list(4)  # Skip 'MTrk'
            length = self._file.read_long()
        else:
            raise IOError('no MTrk header at start of track')

        start = self._file.pos
        last_status = None

        if self.debug:
            _dbg('-> length={}'.format(length))
            _dbg()

        while True:
            # End of track reached.
            if self._file.pos - start == length:
                break

            if self.debug:
                _dbg('Message:')

            delta = self._read_variable_int()
            
            if self.debug:
                _dbg('-> delta={}'.format(delta))

            # Todo: not all messages have running status
            peek_status = self._file.peek_byte()
            if peek_status < 0x80:
                if last_status is None:
                    raise IOError('running status without last_status')
                status_byte = last_status
            else:
                status_byte = self._file.read_byte()
                if status_byte != 0xff:
                    # Meta messages don't set running status.
                    last_status = status_byte

            if status_byte == 0xff:
                message = self._read_meta_message()
            elif status_byte in [0xf0, 0xf7]:
                # Todo: I'm not quite clear on the difference between
                # f0 and f7 events.
                message = self._read_sysex()
            else:
                message = self._read_message(status_byte)

            message.time = delta
            track.append(message)

            if self.debug:
                _dbg('-> {!r}'.format(message))
                _dbg()

        return track

    @property
    def length(self):
        """Playback time in seconds.

        This will be computed by going through every message in every
        track and adding up delta times.
        """
        if self.type == 2:
            raise ValueError('impossible to compute length'
                             ' for type 2 (asynchronous) file')

        return sum(message.time for message in self)

    def _get_seconds_per_tick(self, tempo):
        # Tempo is given in microseconds per beat (default 500000).
        # At this tempo there are (500000 / 1000000) == 0.5 seconds
        # per beat. At the default resolution of 480 ticks per beat
        # this is:
        #
        #    (500000 / 1000000) / 480 == 0.5 / 480 == 0.0010417
        #
        return (tempo / 1000000.0) / self.ticks_per_beat

    def __iter__(self):
        # The tracks of type 2 files are not in sync, so they can
        # not be played back like this.
        if self.type == 2:
            raise TypeError("can't merge tracks in type 2 (asynchronous) file")

        seconds_per_tick = self._get_seconds_per_tick(DEFAULT_TEMPO)

        for message in merge_tracks(self.tracks):
            # Convert message time from absolute time
            # in ticks to relative time in seconds.
            if message.time > 0:
                message.time *= seconds_per_tick
            else:
                message.time = 0

            yield message

            if message.type == 'set_tempo':
                seconds_per_tick = self._get_seconds_per_tick(message.tempo)

    def play(self, meta_messages=False):
        """Play back all tracks.

        The generator will sleep between each message by
        default. Messages are yielded with correct timing. The time
        attribute is set to the number of seconds slept since the
        previous message.

        By default you will only get normal MIDI messages. Pass
        meta_messages=True if you also want meta messages.

        You will receive copies of the original messages, so you can
        safely modify them without ruining the tracks.

        """
        sleep = time.sleep

        for message in self:
            sleep(message.time)

            if isinstance(message, MetaMessage) and not meta_messages:
                continue
            else:
                yield message

    def _has_end_of_track(self, track):
        """Return True if there is an end_of_track at the end of the track."""
        last_i = len(track) - 1
        for i, message in enumerate(track):
            if message.type == 'end_of_track':
                if i != last_i:
                    raise ValueError('end_of_track not at end of the track')
                return True
        else:
            return False

    def save(self, filename=None, file=None):
        """Save to a file.

        If file is passed the data will be saved to that file. This is typically
        an in-memory file or and already open file like sys.stdout.

        If filename is passed the data will be saved to that file.

        Raises ValueError if both file and filename are None,
        or if a type 0 file has != one track.
        """
        if self.type == 0 and len(self.tracks) != 1:
            raise ValueError('type 0 file must have exactly 1 track')

        if file is not None:
            self._save(file)
        elif filename is not None:
            with io.open(filename, 'wb') as file:
                self._save(file)
        else:
            raise ValueError('requires filename or file')

    def _save(self, outfile):
        with meta_charset(self.charset):
            header = struct.pack('>hhh', self.type,
                                 len(self.tracks),
                                 self.ticks_per_beat)

            _write_chunk(outfile, b'MThd', header)

            for track in self.tracks:
                data = bytearray()

                running_status_byte = None
                for message in track:
                    if not isinstance(message, MetaMessage):
                        if message._spec.status_byte >= 0xf8:
                            raise ValueError(
                                ("realtime message '{}' is not "
                                 "allowed in a MIDI file".format(
                                        message.type)))

                    data.extend(encode_variable_int(message.time))
                    if message.type == 'sysex':
                        running_status_byte = None
                        data.append(0xf0)
                        # length (+ 1 for end byte (0xf7))
                        data.extend(encode_variable_int(len(message.data) + 1))
                        data.extend(message.data)
                        data.append(0xf7)
                    else:
                        raw = message.bytes()
                        if (isinstance(message, Message)
                            and raw[0] < 0xf0
                            and raw[0] == running_status_byte):
                            data.extend(raw[1:])
                        else:
                            data.extend(raw)
                        running_status_byte = raw[0]

                if not self._has_end_of_track(track):
                    # Write end_of_track.
                    data.append(0)  # Delta time.
                    data.extend(MetaMessage('end_of_track').bytes())

                _write_chunk(outfile, b'MTrk', data)

    def print_tracks(self, meta_only=False):
        """Prints out all messages in a .midi file.

        May take argument meta_only to show only meta messages.

        Use:
        print_tracks() -> will print all messages
        print_tracks(meta_only=True) -> will print only MetaMessages
        """
        for i, track in enumerate(self.tracks):
            print('=== Track {}'.format(i))
            for message in track:
                if not isinstance(message, MetaMessage) and meta_only:
                    pass
                else:
                    print('{!r}'.format(message))

    def __repr__(self):
        return '<midi file {!r} type {}, {} tracks, {} messages>'.format(
            self.filename, self.type, len(self.tracks),
            sum([len(track) for track in self.tracks]))


    # The context manager has no purpose but is kept around since it was
    # used in examples in the past.
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False
