"""
MIDI file reading and playback.

Todo:
    - make it more fault tolerant (handle errors in MIDI files?)
    - 'reset' message should not be allowed in MIDI file.
      (Does this apply to all real time messages?)
    - handle different character encodings (in strings inside meta messages).

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
import sys
import time
import timeit
import string
from contextlib import contextmanager
from .ports import BaseOutput
from .types import encode_variable_int
from .messages import build_message, Message, get_spec
from .midifiles_meta import MetaMessage, _build_meta_message, meta_charset
from .midifiles_meta import MetaSpec, add_meta_spec
from . import midifiles_meta

# The default tempo is 120 BPM.
# (500000 microseconds per beat (quarter note).)
DEFAULT_TEMPO = 500000

class ByteReader(object):
    """
    Reads bytes from a file.
    """
    def __init__(self, filename):
        self._buffer = list(bytearray(open(filename, 'rb').read()))
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

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False


class ByteWriter(object):
    def __init__(self, filename):
        self.file = open(filename, 'wb')
    
    def write(self, bytes):
        self.file.write(bytearray(bytes))

    def write_byte(self, byte):
        self.file.write(chr(byte))

    def write_short(self, n):
        a = n >> 8
        b = n & 0xff
        self.write([a, b])

    def write_long(self, n):
        a = n >> 24 & 0xff
        b = n >> 16 & 0xff
        c = n >> 8 & 0xff
        d = n & 0xff
        self.write([a, b, c, d])

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.file.close()
        return False

class MidiTrack(list):
    def __init__(self):
        list.__init__([])

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

    def __repr__(self):
        return '<midi track {!r} {} messages>'.format(self.name, len(self))


class MidiFile:
    def __init__(self, filename=None, type=1, ticks_per_beat=480,
                 charset='latin1'):
        self.filename = filename
        self.tracks = []
        self.charset = charset

        if filename is None:
            if type not in range(3):
                raise ValueError(
                    'invalid format {} (must be 0, 1 or 2)'.format(format))
            self.type = type
            self.ticks_per_beat = ticks_per_beat
        else:
            self._load()

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

    def _load(self):
        with ByteReader(self.filename) as self._file, \
                meta_charset(self.charset):
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

            # Skip the rest of the header.
            for _ in range(header_size - 6):
                self._file.read_byte()

            for i in range(number_of_tracks):
                self.tracks.append(self._read_track())
                # Todo: used to ignore EOFError. I hope things still work.

    def _read_variable_int(self):
        delta = 0

        while 1:
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

        magic = self._file.peek_list(4)
        if bytearray(magic) == bytearray(b'MTrk'):
            self._file.read_list(4)  # Skip 'MTrk'
            length = self._file.read_long()
        else:
            # Todo: some files don't have track headers?
            # These end with end_of_track or end of file,
            # so we set length to infinite.
            # raise IOError("track doesn't start with 'MTrk'")
            length = float('inf')

        start = self._file.pos
        last_status = None

        while 1:
            # End of track reached.
            if self._file.pos - start == length:
                break

            delta = self._read_variable_int()

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

            if message.type == 'end_of_track':
                break

        return track

    def _merge_tracks(self, tracks):
        """Merge all messates from tracks.

        Delta times are converted to absolute time (in ticks), and
        messages from all tracks are sorted on absolute time."""
        messages = []
        for i, track in enumerate(self.tracks):
            now = 0
            for message in track:
                if message.type == 'end_of_track':
                    break
                now += message.time
                messages.append(message.copy(time=now))

        messages.sort(key=lambda x: x.time)

        return messages

    def _compute_tick_time(self, tempo):
        """Compute seconds per tick."""
        return (tempo / 1000000.0) / self.ticks_per_beat

    @property
    def length(self):
        """
        Playback time in seconds.

        This will be computed by going through every message in every
        track and adding up delta times.
        """
        # Todo: should fail if type == 2.
        #       (There's no way to know where each track starts.)

        if self.type == 2:
            raise ValueError('impossible to compute length'
                             ' for type 2 (asynchronous) file')

        if not self.tracks:
            return 0.0

        track_lengths = []
    
        for track in self.tracks:
            seconds_per_tick = self._compute_tick_time(500000)
            length = 0.0
            for message in track:
                length += (message.time * seconds_per_tick)
                if message.type == 'set_tempo':
                    seconds_per_tick = self._compute_tick_time(message.tempo)
            track_lengths.append(length)

        return max(track_lengths)

    def __iter__(self):
        # The tracks of type 2 files are not in sync, so they can
        # not be played back like this.
        if self.type == 2:
            raise TypeError('type 2 file can not be played back like this')

        seconds_per_tick = self._compute_tick_time(DEFAULT_TEMPO)
        messages = self._merge_tracks(self.tracks)

        now = 0
        for message in messages:
            delta = (message.time - now) * seconds_per_tick
            if delta >= 0:
                message.time = delta
            else:
                message.time = 0.0

            yield message

            now += delta
            if message.type == 'set_tempo':
                seconds_per_tick = self._compute_tick_time(message.tempo)

    def play(self, meta_messages=False):
        """Play back all tracks.

        The generator will sleep between each message by
        default. Messages are yielded with correct timing. The time
        attribute is set to the number of seconds slept since the
        previous message.

        If you pass sleep=False, the generator will not sleep between
        messages. The messages will still be tagged with the number of
        seconds it would have slept.

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

    def save(self, filename=None):
        """Save to a file.

        If filename is passed, self.filename will be set to this
        value, and the data will be saved to this file. Otherwise
        self.filename is used.

        Raises ValueError both filename and self.filename are None,
        or if a type 1 file has != one track.
        """
        if self.type == 0 and len(self.tracks) != 1:
            raise ValueError('type 1 file must have exactly 1 track')

        if filename is self.filename is None:
            raise ValueError('no file name')

        if filename is not None:
            self.filename = filename

        with ByteWriter(self.filename) as self._file, \
              meta_charset(self.charset):
            self._file.write(b'MThd')

            self._file.write_long(6)  # Header size. (Next three shorts.)
            self._file.write_short(self.type)
            self._file.write_short(len(self.tracks))
            self._file.write_short(self.ticks_per_beat)

            for track in self.tracks:
                bytes = []
                for message in track:
                    if not isinstance(message, MetaMessage):
                        if message._spec.status_byte >= 0xf8:
                            raise ValueError(
                                ("realtime message '{}' is not "
                                 "allowed in a MIDI file".format(
                                        message.type)))

                    # Todo: running status?
                    bytes += encode_variable_int(message.time)
                    if message.type == 'sysex':
                        bytes += [0xf0]
                        # length (+ 1 for end byte (0xf7))
                        bytes += encode_variable_int(len(message.data) + 1)
                        bytes += message.data
                        bytes += [0xf7]
                    else:
                        bytes += message.bytes()

                if not self._has_end_of_track(track):
                    # Write end_of_track.
                    bytes += [0]  # Delta time.
                    bytes += MetaMessage('end_of_track').bytes()

                self._file.write(b'MTrk')
                self._file.write_long(len(bytes))
                self._file.write(bytes)
              
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
 
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

class _DebugByteReader(ByteReader):
    parent = ByteReader

    def _print_bytes(self, n):
        """Print the next n bytes as hex and characters.

        This is used for debugging.
        """
        data = self._buffer[self.pos:self.pos + n]
        print()
        for pos, byte in enumerate(data, start=self.pos):
            char = chr(byte)
            if not char in string.printable or char in string.whitespace:
                char = ''
            print('  {:06x}: {:02x} {}'.format(pos, byte, char))

        if len(data) < n:
            raise EOFError('unexpected end of file')

    def read_byte(self):
        self._print_bytes(1)
        return self.parent.read_byte(self)

    def read_short(self):
        self._print_bytes(2)
        return self.parent.read_short(self)

    def read_long(self):
        self._print_bytes(4)
        return self.parent.read_long(self)

    def read_list(self, n):
        self._print_bytes(n)
        return self.parent.read_list(self, n)

class _DebugMidiFile(MidiFile):
    parent = MidiFile

    def _read_track(self):
        print('-- Track', len(self.tracks))
        return self.parent._read_track(self)

    def _read_message(self, status_byte):
        print('( new message:')
        message = self.parent._read_message(self, status_byte)
        print(')', message)
        return message

    def _read_meta_message(self):
        print('( new meta message')
        message = self.parent._read_meta_message(self)
        print(')', message)
        return message

    def _read_sysex(self):
        print('( new sysex message')
        message = self.parent._read_sysex(self)
        print(')', message)
        return message

def debug():
    """Turn on debugging prints."""
    global ByteReader, MidiFile

    ByteReader = _DebugByteReader
    MidiFile = _DebugMidiFile
