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
from .ports import BaseOutput
from .messages import build_message, Message, get_spec
from .midifiles_meta import MetaMessage, _build_meta_message
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
            # print('{:02x}'.format(byte))
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

    def read_list(self, n):
        """Read n bytes and return as a list."""
        i = self.pos
        ret = self._buffer[i:i + n]
        # for byte in ret:
        #     print('  {:02x} {!r}'.format(byte, chr(byte)))
        if len(ret) < n:
            raise self._eof

        self.pos += n
        return ret

    def read_short(self):
        """Read short (2 bytes little endian)."""
        a, b = self.read_list(2)
        return a << 8 | b

    def read_long(self):
        """Read long (4 bytes little endian)."""
        a, b, c, d = self.read_list(4)
        return a << 24 | b << 16 | c << 8 | d

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


class DeltaTimer(object):
    def __init__(self, midifile=None, ticks_per_beat=None, tempo=500000):
        self.midifile = None
        if self.midifile:
            self.ticks_per_beat = midifile.ticks_per_beat
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.timer = timeit.default_timer
        self.then = self.timer()

    def __call__(self):
        now = self.timer()
        delta = now - self.then
        self.then = now
        
        if self.ticks_per_beat is not None:
            seconds_per_beat = self.tempo / 1000000.0
            seconds_per_tick = seconds_per_beat / float(self.ticks_per_beat)
            new_delta = int(delta / seconds_per_tick)
            return new_delta

        return delta


class MidiTrack(list):
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


class RecordPort(BaseOutput):
    def __init__(self, midifile):
        BaseOutput.__init__(self)
        self.midifile = midifile
        self.delta = DeltaTimer(ticks_per_beat=midifile.ticks_per_beat,
                               tempo=DEFAULT_TEMPO)
        self.track = self.midifile.add_track()
    
    def send(self, message):
        # This overrides the public send() because the
        # original one doesn't accept meta messages.
        self.track.append(message.copy(time=self.delta()))
        if message.type == 'set_tempo':
            self.delta.tempo = message.tempo

    def _close(self):
        self.track.append(MetaMessage('end_of_track'))


class MidiFile:
    def __init__(self, name=None, format=1, ticks_per_beat=None,
                 charset='latin1'):
        self.name = name
        self.tracks = []
        self.charset = charset

        if name is None:
            if format not in range(3):
                raise ValueError(
                    'invalid format {} (must be 0, 1 or 2)'.format(format))
            self.format = format
            # Todo: is this a good default value?
            self.ticks_per_beat = 120
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
        midifiles_meta._charset = self.charset

        with ByteReader(self.name) as self._file:
            # Read header (16 bytes)
            magic = self._file.read_list(4)
            if not bytearray(magic) == bytearray(b'MThd'):
                raise IOError('MThd not found. Probably not a MIDI file')

            # This is always 6 for any file created under the MIDI 1.0
            # specification, but this allows for future expansion.
            header_size = self._file.read_long()

            self.format = self._file.read_short()
            number_of_tracks = self._file.read_short()
            self.ticks_per_beat = self._file.read_short()

            # Skip the rest of the header.
            for _ in range(header_size - 6):
                self._file.read_byte()

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
        try:
            spec = get_spec(status_byte)
        except LookupError:
            raise IOError('undefined status byte 0x{:02x}'.format(status_byte))
        data_bytes = self._file.read_list(spec.length - 1)
        for byte in data_bytes:
            if byte > 127:
                raise IOError('data byte has value > 127')
        return build_message(spec, [status_byte] + data_bytes)

    def _read_meta_message(self):
        type = self._file.read_byte()
        length = self._file.read_byte()
        data = self._file.read_list(length)
        return _build_meta_message(type, data)

    def _read_sysex(self):
        length = self._file.read_byte()
        data = self._file.read_list(length)

        if data and data[-1] == 0xf7:
            data = data[:-1]

        message = Message('sysex', data=data)
        return message

    def _read_track(self):
        track = MidiTrack()

        magic = self._file.read_list(4)
        if bytearray(magic) != bytearray(b'MTrk'):
            raise IOError("track doesn't start with 'MTrk'")

        length = self._file.read_long()
        start = self._file.pos
        last_status = None
        last_systex = None

        while 1:
            # End of track reached.
            if self._file.pos - start == length:
                break

            delta = self._read_delta_time()

            # Todo: not all messages have running status
            peek_status = self._file.peek_byte()
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
                # Todo: check if this works as intended.
                if last_systex is None:
                    raise IOError(
                        'sysex continuation without preceding sysex')
                last_sysex.data += self._read_sysex()
                continue
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

    def play(self, meta_messages=False):
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

            if meta_messages or isinstance(message, Message):
                message.time = sleep_time
                yield message

            now += delta
            if message.type == 'set_tempo':
                seconds_per_tick = self._compute_tick_time(message.tempo)

    def _encode_delta_time(self, delta):
        bytes = []
        while delta:
            bytes.append(delta & 0x7f)
            delta >>= 7
        
        if bytes:
            bytes.reverse()

            # Set high bit in every byte but the last.
            for i in range(len(bytes) - 1):
                bytes[i] |= 0x80
            return bytes
        else:
            return [0]

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
        midifiles_meta._charset = self.charset

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
                    if not isinstance(message, MetaMessage):
                        if message._spec.status_byte >= 0xf8:
                            raise ValueError(
                                ("realtime message '{}' is not "
                                 "allowed in a MIDI file".format(
                                        message.type)))

                    # Todo: running status?
                    bytes += self._encode_delta_time(message.time)
                    bytes += message.bytes()

                if not self._has_end_of_track(track):
                    # Write end_of_track.
                    bytes += self._encode_delta_time(0)
                    bytes += MetaMessage('end_of_track').bytes()

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

    def print_tracks(self, showOnlyMetaMessages=False):
        # Todo: The argument "showOnlyMetaMessages" does not work as expected. Most likely an easy tweak is still required.
        """Prints out all messages in a .midi file.

        May take argument showOnlyMetaMessages to show only meta messages.

        Use:
        MidiFile.print_tracks() -> will print all messages
        MidiFile.print_tracks(showOnlyMetaMessages) -> will print only MetaMessages
        """
        for i, track in enumerate(self.tracks):
            sys.stdout.write('=== Track {}\n'.format(i))
            for message in track:
                if not isinstance(message, MetaMessage) and showOnlyMetaMessages:
                    pass
                else:
                    sys.stdout.write('  {!r}\n'.format(message))
                
