# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import io

from pytest import raises

from mido.file.smf.event import MetaEvent, MidiEvent
from mido.file.smf.event.meta import KeySignatureError
from mido.file.smf.midifile import MidiFile, MidiTrack

HEADER_ONE_TRACK = """
4d 54 68 64  # Chunk type: MThd (Header)
00 00 00 06  # Chunk size: 6
      00 01  # Format: 1
      00 01  # Number of tracks: 1
      00 78  # Resolution: 120 ticks per beat
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
    4d 54 68 64  # Chunk type: MThd (Header)
    00 00 00 06  # Chunk size: 6
    00 01        # Type: 1
    00 00        # Number of tracks: 0
    00 78        # Resolution: 120 ticks per beat
    """).tracks == []


def test_single_event():
    assert read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b  # Chunk type: MTrk (Track)
    00 00 00 04  # Chunk size: 4
    20           # Event delta-time : 32
    90 40 40     # Message event: note_on channel=0 note=64 velocity=64
    """).tracks[0][0] == MidiEvent(delta_time=32,
                                   type='note_on', note=64, velocity=64)


def test_too_long_event():
    with raises(IOError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b       # Chunk type: MTrk (Track)
        00 00 00 04       # Chunk size: 4
        00                # Event delta-time: 0
        ff 03 ff ff 7f    # Meta event: track_name extremely long
        """)


def test_two_tracks():
    mid = read_file("""
    4d54 6864 0000 0006 0001 0002 0040             # Header
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
        4d 54 72 6b  # Chunk type: MTrk (Track)
        00 00 00 01  # Chunk size: 1
        # Oops, no data here.
        """)


def test_invalid_data_byte_no_clipping():
    # TODO: should this raise IOError?
    with raises(IOError):
        read_file(HEADER_ONE_TRACK + """
        4d 54 72 6b  # Chunk type: MTrk (Track)
        00 00 00 04  # Chunk size: 4
        00           # Event delta-time: 0
        90 ff 40     # Message event: note_on channel=0 note=255 velocity=64
        """)


def test_invalid_data_byte_with_clipping_high():
    midi_file = read_file(HEADER_ONE_TRACK + """
      4d 54 72 6b  # Chunk type: MTrk (Track)
      00 00 00 04  # Chunk size: 4
      00           # Event delta-time: 0
      90 ff 40     # Message event: note_on channel=0 note=255 velocity=64
                          """, clip=True)
    assert midi_file.tracks[0][0].note == 127


def test_meta_events():
    # TODO: should this raise IOError?
    mid = read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b              # Chunk type: MTrk (Track)
    00 00 00 0c              # Chunk size: 12
    00                       # Event delta-time: 0
    ff 03 04 54 65 73 74     # Meta event: track_name name='Test'
    00                       # Event delta-time: 0
    ff 2f 00                 # Meta event: end_of_track
    """)

    track = mid.tracks[0]

    assert track[0] == MetaEvent(delta_time=0, type='track_name', name='Test')
    assert track[1] == MetaEvent(delta_time=0, type='end_of_track')


def test_meta_event_bad_key_sig_throws_key_signature_error_sharps():
    with raises(KeySignatureError):
        read_file(HEADER_ONE_TRACK + """
            4d 54 72 6b     # Chunk type: MTrk (Track)
            00 00 00 09     # Chunk size: 9
            00              # Event delta-time: 0
            ff 59 02 08     # Meta event: Key Signature with 8 sharps
            00              # Event delta-time: 0
            ff 2f 00        # Meta event: end_of_track
            """)


def test_meta_event_bad_key_sig_throws_key_signature_error_flats():
    with raises(KeySignatureError):
        read_file(HEADER_ONE_TRACK + """
            4d 54 72 6b     # Chunk type: MTrk (Track)
            00 00 00 09     # Chunk size: 9
            00              # Event delta-time: 0
            ff 59 02 f8     # Meta event: Key Signature with 8 flats
            00              # Event delta-time: 0
            ff 2f 00        # Meta event: end_of_track
            """)


def test_meta_events_with_length_0():
    """sequence_number and midi_port with no data bytes should be accepted.

    In rare cases these events have length 0 and thus no data
    bytes. (See issues 42 and 93.) It is unclear why these events
    are missing their data. It could be cased by a bug in the software
    that created the files.

    So far this has been fixed by adding a test to each of these two
    meta event classes. If the problem appears with other event
    types it may be worth finding a more general solution.
    """
    mid = read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b         # Chunk type: MTrk
    00 00 00 17         # Chunk size: 23

    00 ff 00 00         # Meta event: delta_time=0
                        #             sequence_number
                        #             with no data bytes (should be 2).

    00 ff 21 00         # Meta event: delta_time=0
                        #             midi_port
                        #             with no data bytes (should be 1).

    00 ff 00 02 00 01   # Meta event: delta_time=0
                        #             sequence_number
                        #             with correct number of data bytes (2).

    00 ff 21 01 01      # Meta event: delta_time=0
                        #             midi_port
                        #             with correct number of data bytes (1).

    00 ff 2f 00         # Meta event: delta_time=0
                        #             end_of_track
    """)

    assert mid.tracks[0] == [
        MetaEvent(delta_time=0, type='sequence_number', number=0),
        MetaEvent(delta_time=0, type='midi_port', port=0),

        MetaEvent(delta_time=0, type='sequence_number', number=1),
        MetaEvent(delta_time=0, type='midi_port', port=1),

        MetaEvent(delta_time=0, type='end_of_track'),
    ]


def test_midifile_repr():
    midifile = MidiFile(type=1, ticks_per_beat=123, tracks=[
        MidiTrack([
            MidiEvent(delta_time=3, type='note_on', channel=1, note=2),
            MidiEvent(delta_time=3, type='note_off', channel=1, note=2)]),
        MidiTrack([
            MetaEvent(delta_time=0, type='sequence_number', number=5),
            MidiEvent(delta_time=9, type='note_on', channel=2, note=6),
            MidiEvent(delta_time=9, type='note_off', channel=2, note=6)]),
    ])
    midifile_eval = eval(repr(midifile))  # noqa: S307
    for track, track_eval in zip(midifile.tracks, midifile_eval.tracks):
        for m1, m2 in zip(track, track_eval):
            assert m1 == m2
