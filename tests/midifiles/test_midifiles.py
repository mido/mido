# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import io
import os

from pytest import mark, raises

from mido.messages import Message
from mido.midifiles.meta import KeySignatureError, MetaMessage
from mido.midifiles.midifiles import MidiFile, MidiTrack

HEADER_ONE_TRACK = """
4d 54 68 64  # MThd
00 00 00 06  # Chunk size
      00 01  # Type 1
      00 01  # 1 track
      00 78  # 120 ticks per beat
"""


def parse_hexdump(hexdump):
    data = bytearray()
    for line in hexdump.splitlines():
        data += bytearray.fromhex(line.split('#')[0])
    return data


def read_file(hexdump, clip=False):
    return MidiFile(file=io.BytesIO(parse_hexdump(hexdump)), clip=clip)


def test_no_tracks():
    assert read_file("""
    4d 54 68 64  # MThd
    00 00 00 06  # Chunk size
    00 01  # Type 1
    00 00  # 0 tracks
    00 78  # 120 ticks per beat
    """).tracks == []


def test_single_message():
    assert read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b  # MTrk
    00 00 00 04
    20 90 40 40  # note_on
    """).tracks[0] == [Message('note_on', note=64, velocity=64, time=32)]


def test_too_long_message():
    with raises(IOError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 04
        00 ff 03 ff ff 7f # extremely long track name message
        """)


def test_two_tracks():
    mid = read_file("""
    4d54 6864 0000 0006 0001 0002 0040        # Header
    4d54 726b 0000 0008 00 90 40 10  40 80 40 10   # Track 0
    4d54 726b 0000 0008 00 90 47 10  40 80 47 10   # Track 1
    """)
    assert len(mid.tracks) == 2
    # TODO: add some more tests here.


def test_empty_file():
    with raises(EOFError):
        read_file("")


def test_eof_in_track():
    with raises(EOFError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 01  # Chunk size
        # Oops, no data here.
        """)


def test_invalid_data_byte_no_clipping():
    # TODO: should this raise IOError?
    with raises(IOError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 04  # Chunk size
        00 90 ff 40  # note_on note=255 velocity=64
        """)


def test_invalid_data_byte_with_clipping_high():
    midi_file = read_file(HEADER_ONE_TRACK + """
                          4d 54 72 6b  # MTrk
                          00 00 00 04  # Chunk size
                          00 90 ff 40  # note_on note=255 velocity=64
                          """, clip=True)
    assert midi_file.tracks[0][0].note == 127


def test_meta_messages():
    # TODO: should this raise IOError?
    mid = read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b  # MTrk
    00 00 00 0c  # Chunk size
    00 ff 03 04 54 65 73 74  # track_name name='Test'
    00 ff 2f 00  # end_of_track
    """)

    track = mid.tracks[0]

    assert track[0] == MetaMessage('track_name', name='Test')
    assert track[1] == MetaMessage('end_of_track')


def test_meta_message_bad_key_sig_throws_key_signature_error_sharps():
    with raises(KeySignatureError):
        read_file(HEADER_ONE_TRACK + """
            4d 54 72 6b  # MTrk
            00 00 00 09  # Chunk size
            00 ff 59 02 08 # Key Signature with 8 sharps
            00 ff 2f 00  # end_of_track
            """)


def test_meta_message_bad_key_sig_throws_key_signature_error_flats():
    with raises(KeySignatureError):
        read_file(HEADER_ONE_TRACK + """
            4d 54 72 6b  # MTrk
            00 00 00 09  # Chunk size
            00 ff 59 02 f8 # Key Signature with 8 flats
            00 ff 2f 00  # end_of_track
            """)


def test_meta_messages_with_length_0():
    """sequence_number and midi_port with no data bytes should be accepted.

    In rare cases these messages have length 0 and thus no data
    bytes. (See issues 42 and 93.) It is unclear why these messages
    are missing their data. It could be cased by a bug in the software
    that created the files.

    So far this has been fixed by adding a test to each of these two
    meta message classes. If the problem appears with other message
    types it may be worth finding a more general solution.
    """
    mid = read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b  # MTrk
    00 00 00 17

    00 ff 00 00  # sequence_number with no data bytes (should be 2).
    00 ff 21 00  # midi_port with no data bytes (should be 1).

    00 ff 00 02 00 01  # sequence_number with correct number of data bytes (2).
    00 ff 21 01 01     # midi_port with correct number of data bytes (1).

    00 ff 2f 00
    """)

    assert mid.tracks[0] == [
        MetaMessage('sequence_number', number=0),
        MetaMessage('midi_port', port=0),

        MetaMessage('sequence_number', number=1),
        MetaMessage('midi_port', port=1),

        MetaMessage('end_of_track'),
    ]


def test_midifile_repr():
    midifile = MidiFile(type=1, ticks_per_beat=123, tracks=[
        MidiTrack([
            Message('note_on', channel=1, note=2, time=3),
            Message('note_off', channel=1, note=2, time=3)]),
        MidiTrack([
            MetaMessage('sequence_number', number=5),
            Message('note_on', channel=2, note=6, time=9),
            Message('note_off', channel=2, note=6, time=9)]),
    ])
    midifile_eval = eval(repr(midifile))  # noqa: S307
    for track, track_eval in zip(midifile.tracks, midifile_eval.tracks):
        for m1, m2 in zip(track, track_eval):
            assert m1 == m2


class ReadOnlyStream:
    """A forward-only input supporting read(), but not tell() or seek()."""

    def __init__(self, data):
        self.stream = io.BytesIO(data)

    def read(self, size):
        assert size >= 0  # Do not buffer the entire input.
        return self.stream.read(size)


STREAMING_FILE = """
4d54 6864 0000 0006 0001 0003 0078  # Three tracks
4d54 726b 0000 0000                 # Empty track
4d54 726b 0000 0014                 # Track with premature/repeated EOT
00 ff 2f 00                        # Premature end_of_track
20 90 40 40                        # note_on
00 41 20                           # Running status note_on
00 f0 02 01 f7                     # sysex
00 ff 2f 00                        # end_of_track
4d54 726b 0000 0004                 # Track without an end_of_track
10 80 40 00                        # note_off
"""


@mark.parametrize('debug', [False, True])
@mark.parametrize('stream_type', [io.BytesIO, ReadOnlyStream])
def test_read_forward_only_stream(stream_type, debug):
    trailer = b'not part of the MIDI file'
    stream = stream_type(bytes(parse_hexdump(STREAMING_FILE)) + trailer)
    midi = MidiFile(file=stream, debug=debug)

    assert midi.ticks_per_beat == 120
    assert midi.tracks == [
        [],
        [MetaMessage('end_of_track'),
         Message('note_on', note=64, velocity=64, time=32),
         Message('note_on', note=65, velocity=32),
         Message('sysex', data=[1]),
         MetaMessage('end_of_track')],
        [Message('note_off', note=64, velocity=0, time=16)],
    ]
    assert stream.read(len(trailer)) == trailer


@mark.parametrize('debug', [False, True])
def test_read_midi_pipe(debug):
    data = bytes(parse_hexdump(STREAMING_FILE))
    read_fd, write_fd = os.pipe()
    with os.fdopen(read_fd, 'rb') as source:
        with os.fdopen(write_fd, 'wb') as destination:
            destination.write(data)
        assert not source.seekable()
        midi = MidiFile(file=source, debug=debug)
        assert midi.tracks == MidiFile(file=io.BytesIO(data)).tracks
        assert not source.closed


@mark.parametrize('debug', [False, True])
def test_truncated_forward_only_stream(debug):
    data = bytes(parse_hexdump(STREAMING_FILE))
    with raises(EOFError):
        MidiFile(file=ReadOnlyStream(data[:-1]), debug=debug)
