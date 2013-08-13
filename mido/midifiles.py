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
import mido
from collections import deque
from .messages import BaseMessage

class ByteReader(object):
    def __init__(self, stream):
        self.stream = stream
        self.data = deque()

        for line in stream:
            self.data.extend(bytearray(line))

        self._pos = 0

    def read_list(self, n):
        return [self.read_byte() for _ in range(n)]

    def read_bytes(self, n):
        return bytes(self.read_list(n))

    def read_bytearray(self, n):
        return bytearray(self.read_list(n))

    def read_byte(self):
        """Get the next byte from."""
        try:
            self._pos += 1
            return self.data.popleft()
        except IndexError:
            raise EOFError('end of file reached')

    def put_back_byte(self, byte):
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


def dbg(*args):
    print(*args)


def dbg2(*args):
    print(*args)


class FileReader(ByteReader):
    def read_byte(self):
        byte = ByteReader.read_byte(self)
        # dbg('{:02x} @ {:02x}'.format(byte, self.tell()))
        return byte

    def put_back_byte(self, byte):
        byte = ByteReader.put_byte_back(self, byte)
        # dbg('{:02x} put back'.format(byte))

    def read_short(self):
        a, b = [self.read_byte() for i in range(2)]
        return a << 8 | b

    def read_long(self):
        a, b, c, d = [self.read_byte() for i in range(4)]
        return a << 24 | b << 16 | c << 8 | d


class EndOfTrack(IOError):
    pass


class MetaMessage(BaseMessage):
    def __init__(self, type, data):
        self.type = 'meta'
        self.meta_type = type
        self.data = data
        self.time = 0

    def __repr__(self):
        return '<meta message type={}, data={!r}, time={}>'.format(
            self.meta_type, self.data, self.time)


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

            # dbg('--- File format: {}'.format(self.file_format))

            self._read_tracks()
        
    def _print_tracks(self):
        for i, track in enumerate(self.tracks):
            print('=== Track {}'.format(i))
            for event in track:
                print('  ', repr(event))

    def _read_delta_time(self):
        delta = 0

        while 1:
            byte = self.file.read_byte()
            delta = (delta << 7) | (byte & 0x7)
            if not byte & 0x80:
                break

        # dbg('    delta time', delta)
        return delta

    def _read_meta_event(self):
        type = self.file.read_byte()
        length = self.file.read_byte()
        data = self.file.read_bytes(length)

        # dbg('    meta event {:02x} {} {!r}'.format(type, length, data))
        event = MetaMessage(type, data)
        if type == 0x2f:
            # dbg('    found end of track')
            raise EndOfTrack('end of track found')

        return event


    def _read_message(self, status_byte):
        # dbg('+')

        # Todo: not all messages have running status
        if status_byte < 0x80:
            # dbg('    --- {}'.format('running status'))
            if self._running_status is None:
                # dbg('    *** {}'.format('no previous status byte!'))
                return
            status_byte = self._running_status
            # self.file.put_back_byte(status_byte)
        else:
            self._running_status = status_byte

        try:
            spec = mido.messages.get_spec(status_byte)
        except LookupError:
            # dbg2('    *** unknown status byte {:02x}'.format(status_byte))
            sys.exit(1)

        bytes = [status_byte]

        for i in range(spec.length - 1):
            bytes.append(self.file.read_byte())

        # dbg('    bytes for message: {}'.format(bytes))

        # message = mido.parse(bytes)
        message = build_message(spec, bytes)
        # dbg('    {}'.format(message))

        return message


    def _read_sysex(self):
        length = self.file.read_byte()
        data = self.file.read_list(length)
        if data[-1] == 0xf7:
            data = data[:-1]

        message = mido.Message('sysex', data=data)
        # dbg('    {}'.format(message))

        return message


    def _read_event(self, delta):
        status_byte = self.file.read_byte()

        if status_byte == 0xff:
            event = self._read_meta_event()

        elif status_byte == 0xf0:
            event =self._read_sysex()

        elif status_byte == 0xf7:
            event = self._read_sysex()  # Todo: continuation of previous sysex

        else:
            event = self._read_message(status_byte)

        if event is not None:
            event.time = delta
            self._current_track.append(event)


    def _read_track(self):
        magic = self.file.read_bytearray(4)
        if magic != bytearray(b'MTrk'):
            raise ValueError("track doesn't start with 'MTrk'")

        length = self.file.read_long()  # Ignore this.

        # dbg('******** found track of length', length)

        self._current_track = []
        self._running_status = None

        start = self.file.tell()

        while 1:
            try:
                # End of track reached
                if self.file.tell() - start == length:
                    break

                # dbg('    !{} {}'.format(length, self.file.tell() - start))
                delta = self._read_delta_time()
                self._read_event (delta)
            except EndOfTrack:
                break

        self.tracks.append(self._current_track)
        self._current_track = []

    def _read_tracks(self):
        try:
            for i in range(self.number_of_tracks):
                self._read_track()
        except EOFError:
            # dbg('    wrong number of tracks (reached end of file')
            # dbg('    while reading track ')
            # dbg('      {} of {})'.format(i, self.number_of_tracks))
            pass
        # print(self.file.tell())

# mid1/acso3op2.mid:
# 00008b0: 00c0 0604 b05b 5400 5d5d 8168 0a58 0307
#          (prog )(control )(? ... )(note off)(? )
#
# 00008c0: 7f81 4a90 4057 0043 5901 4854 1940 0001
#          (off ?  ) (?                          )
