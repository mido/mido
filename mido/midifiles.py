"""
MIDI file reading and playback.

Todo:
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
from .messages import build_message, Message, get_spec
from .midifiles_meta import MetaMessage

DEBUG_PARSING = bool(os.environ.get('MIDO_DEBUG_PARSING'))

class ByteReader(object):
    """
    Reads bytes from a file.
    """

    # Todo: test if EOFError is raised.

    def __init__(self, filename):
        self.buffer = io.BufferedReader(io.open(filename, 'rb'))
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
        pos = self.tell()
        byte = self.read_byte_list(1)[0]
        if DEBUG_PARSING:
            print('  {:6x}: {:02x}'.format(pos, byte))
        return byte

    def peek_byte(self):
        """Return the next byte in the file.

        This can be used for look-ahead."""
        # Todo: this seems a bit excessive for just one byte.
        byte = bytearray(self.buffer.peek(1))[0]
        if DEBUG_PARSING:
            print(' ({:6x}): peek {:02x}'.format(self.tell(), byte))
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


class MidiFile:
    def __init__(self, filename):
        self.filename = filename
        self.tracks = []

        with ByteReader(filename) as self.file:
            # Read header (16 bytes)
            magic = self.file.read_bytearray(4)
            if not magic == bytearray(b'MThd'):
                raise IOError('not a MIDI file')

            # Skip header size. (It's always 6, referring to the size
            # of the next three shorts.)
            self.file.read_long()

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

    def _compute_tempo(self, tempo):
        """Compute seconds per tick."""
        seconds_per_quarter_note = (tempo / 1000000.0)
        return seconds_per_quarter_note / self.ticks_per_quarter_note

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

        # The default tempo is 120 BPM.
        # (500000 microseconds per quarter note.)
        seconds_per_tick = self._compute_tempo(500000)

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
                seconds_per_tick = self._compute_tempo(message.tempo)

    __iter__ = play

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False
