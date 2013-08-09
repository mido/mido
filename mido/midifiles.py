"""
MIDI file reading and playback.

Todo:
    - make it more fault tolerant (handle errors in MIDI files?)

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
from .messages import build_message, Message, get_spec
from .midifiles_meta import MetaMessage

# The default tempo is 120 BPM.
# (500000 microseconds per beat (quarter note).)
DEFAULT_TEMPO = 500000

class ByteReader(object):
    """
    Reads bytes from a file.
    """
    def __init__(self, filename):
        self._buffer = bytearray(open(filename, 'rb').read())
        self._index = 0

    def _eof(self):
        return 

    def read_bytearray(self, n):
        """Read n bytes and return as a bytearray."""
        i = self._index
        ret = self._buffer[i:i + n]
        if len(ret) < n:
            raise self._eof

        self._index += n
        return ret

    def read_byte_list(self, n):
        """Read n bytes and return as a list."""
        return list(self.read_bytearray(n))

    def read_byte(self):
        """Read one byte."""
        try:
            byte = self._buffer[self._index]
            self._index += 1
            return byte
        except IndexError:
            raise self._eof

    def peek_byte(self):
        """Return the next byte in the file.

        This can be used for look-ahead."""
        try:
            return self._buffer[self._index]
        except IndexError:
            raise self._eof

    def read_short(self):
        """Read short (2 bytes little endian)."""
        a, b = self.read_byte(), self.read_byte()
        return a << 8 | b

    def read_long(self):
        """Read long (4 bytes little endian)."""
        a, b, c, d = self.read_bytearray(4)
        return a << 24 | b << 16 | c << 8 | d

    def tell(self):
        return self._index

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


class Track(list):
    def __init__(self):
        list.__init__([])

    def _get_name(self):
        for message in self:
            if message.type == 'track_name':
                return message.name
        else:
            return u''

    def _set_name(self, name):
        # Find the first track_name message and modify it.
        for message in self:
            if message.type == 'track_name':
                message.name = name
                return
        else:
            # No track name found, add one.
            self.insert(0, MetaMessage('track_name', name=name, time=0))

    name = property(fget=_get_name, fset=_set_name)
    del _get_name, _set_name

    def __repr__(self):
        name = repr(self.name)
        if name.startswith('u'):
            # Python 2.
           name = name[1:]
        return '<midi track {} {} messages>'.format(name, len(self))


class MidiFile:
    def __init__(self, name=None, format=1):
        self.name = name
        self.tracks = []

        if name is None:
            if format not in range(3):
                raise ValueError(
                    'invalid format {} (must be 0, 1 or 2)'.format(format))
            self.format = format
            # Todo: is this a good default value?
            self.ticks_per_beat = 120
        else:
            self._load()

    def _load(self):
        with ByteReader(self.name) as self._file:
            # Read header (16 bytes)
            magic = self._file.read_bytearray(4)
            if not magic == bytearray(b'MThd'):
                raise IOError('MThd not found. Probably not a MIDI file')

            # Skip header size. (It's always 6, referring to the size
            # of the next three shorts.)
            self._file.read_long()

            self.format = self._file.read_short()
            number_of_tracks = self._file.read_short()
            self.ticks_per_beat = self._file.read_short()

            for i in range(number_of_tracks):
                self.tracks.append(self._read_track())
                # Todo: used to ignore EOFError. I hope things still work.

    def _read_delta_time(self):
        delta = 0

        while 1:
            byte = self._file.read_byte()
            delta = (delta << 7) | (byte & 0x7f)
            if byte < 0x80:
                return delta

    def _read_message(self, status_byte):
        spec = get_spec(status_byte)
        bytes = [status_byte] + self._file.read_byte_list(spec.length - 1)
        return build_message(bytes, spec)

    def _read_meta_message(self):
        type = self._file.read_byte()
        length = self._file.read_byte()
        data = self._file.read_byte_list(length)
        return MetaMessage(type, data)

    def _read_sysex(self):
        length = self._file.read_byte()
        data = self._file.read_byte_list(length)

        if data and data[-1] == 0xf7:
            data = data[:-1]

        message = Message('sysex', data=data)
        return message

    def _read_track(self):
        track = Track()

        magic = self._file.read_bytearray(4)
        if magic != bytearray(b'MTrk'):
            raise IOError("track doesn't start with 'MTrk'")

        length = self._file.read_long()
        start = self._file.tell()
        last_status = None
        last_systex = None

        while 1:
            # End of track reached.
            if self._file.tell() - start == length:
                break

            is_sysex_continuation = False

            delta = self._read_delta_time()

            peek_status = self._file.peek_byte()

            # Todo: not all messages have running status
            if peek_status < 0x80:
                if last_status is None:
                    raise IOError('running status without last_status')
                status_byte = last_status
            else:
                status_byte = self._file.read_byte()
                last_status = status_byte

            if status_byte == 0xff:
                message = self._read_meta_message()
            elif status_byte == 0xf0:
                message = self._read_sysex()
                last_sysex = message
            elif status_byte == 0xf7:
                message = self._read_sysex()
                # Todo: does this actually work?
                is_sysex_continuation = True
                if last_systex is None:
                    raise IOError(
                        'sysex continuation without preceding sysex')
                last_systex.data += message.data
            else:
                message = self._read_message(status_byte)

            message.time = delta

            if not is_sysex_continuation:
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

    def _compute_tick_time(self, milliseconds_per_beat):
        """Compute seconds per tick."""
        return (milliseconds_per_beat / 1000000.0) / self.ticks_per_beat

    def _get_length(self):
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

    length = property(fget=_get_length)

    def play(self, yield_meta_messages=False):
        """Play back all tracks.

        The generator will sleep between each message, so that
        messages are yielded with correct timing. The time attribute
        is set to the number of seconds slept since the previous
        message.

        You will receive copies of the original messages, so you can
        safely modify them without ruining the tracks.
        """

        # The tracks of format 2 files are not in sync, so they can
        # not be played back like this.
        if self.format == 2:
            raise ValueError('format 2 file can not be played back like this')

        seconds_per_tick = self._compute_tick_time(DEFAULT_TEMPO)

        messages = self._merge_tracks(self.tracks)

        # Play back messages.
        now = 0
        for message in messages:
            delta = message.time - now
            if delta:
                sleep_time = delta * seconds_per_tick
                time.sleep(sleep_time)
            else:
                sleep_time = 0.0

            if yield_meta_messages or isinstance(message, Message):
                message.time = sleep_time
                yield message

            now += delta
            if message.type == 'set_tempo':
                seconds_per_tick = self._compute_tick_time(message.tempo)

    __iter__ = play

    def _encode_delta_time(self, delta):
        bytes = []
        while 1:
            byte = delta & 0x7f
            bytes.append(byte)

            if byte <= 0x80:
                bytes.reverse()
                return bytes

            delta = delta >> 7

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

        If filename is passed, self.name will be set to this
        value, and the data will be saved to this file. Otherwise
        self.name is used.

        Raises ValueError both filename and self.name are None,
        or if a format 1 file has != one track.
        """

        if self.format == 0 and len(self.tracks) != 1:
            raise ValueError('format 1 file must have exactly 1 track')

        if filename is self.name is None:
            raise ValueError('no file name')

        if filename is not None:
            self.name = filename

        with ByteWriter(self.name) as self._file:
            self._file.write(b'MThd')

            self._file.write_long(6)  # Header size. (Next three shorts.)
            self._file.write_short(self.format)
            self._file.write_short(len(self.tracks))
            self._file.write_short(self.ticks_per_beat)

            for track in self.tracks:
                bytes = []
                for message in track:
                    # Todo: support meta messages.
                    if isinstance(message, MetaMessage):
                        if message.type == 'end_of_track':
                            # Write end of track.
                            bytes += self._encode_delta_time(message.time)
                            bytes += [0xff, 0x2f, 0]
                        else:
                            # Todo: implement bytes() method in MetaMessage.
                            # For now just skip this message.
                            continue
                    else:
                        # Todo: running status?
                        bytes += self._encode_delta_time(message.time)
                        bytes += message.bytes()

                if not self._has_end_of_track(track):
                    # Write end_of_track.
                    bytes += self._encode_delta_time(0)
                    bytes += [0xff, 0x2f, 0]

                self._file.write(b'MTrk')
                self._file.write_long(len(bytes))
                self._file.write(bytes)
              
    def __repr__(self):
        name = repr(self.name)
        if name.startswith('u'):
            # Python 2.
            name = name[1:]
        return '<midi file {} format {}, {} tracks, {} messages>'.format(
            name, self.format, len(self.tracks),
            sum([len(track) for track in self.tracks]))
 
    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False
