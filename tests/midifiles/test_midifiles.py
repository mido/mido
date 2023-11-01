# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import io

import pytest
from pytest import raises
from mido.messages import Message
from mido.midifiles.midifiles import MidiFile, MidiTrack
from mido.midifiles.meta import MetaMessage, KeySignatureError

_MINIMAL_SPEC_COMPLIANT_HEADER = """
4D 54 68 64  # Chunk type       SMF Header ('MThd')
00 00 00 06  # Chunk length     6
      00 00  # Format           0
      00 01  # Number of tracks 1
      00 60  # Division         96 per quarter-note
"""

_MINIMAL_SPEC_COMPLIANT_TRACK = """
4D 54 72 6B  # Chunk type           SMF Track ('MTrk')
00 00 00 13  # Chunk length         19
         # Event 0
         00  # Delta-time           0
         FF  # Event                Meta
         58  # Meta-event type      Time Signature
         04  # Meta-event length    4
06 03 24 08  # Meta-event bytes     6/8
         # Event 1
         00  # Delta-time           0
         FF  # Event                Meta
         51  # Meta-event type      Set Tempo
         03  # Meta-event length    0
   07 A1 20  # Meta-event bytes     500 000 us/qn <=> 120 BPM
         # Event 2
         00  # Delta-time           0
         FF  # Event                Meta
         2F  # Meta-event type      End of Track
         00  # Meta-event length    0
"""

_DECODED_MINIMAL_SPEC_COMPLIANT_TRACK = [
    MetaMessage('time_signature',
                numerator=6, denominator=8,
                clocks_per_click=36, notated_32nd_notes_per_beat=8,
                time=0),
    MetaMessage('set_tempo', tempo=500_000, time=0),
    MetaMessage('end_of_track', time=0)
]

_HEADER_ONE_TRACK = """
4d 54 68 64  # Chunk type       SMF Header ('MThd')
00 00 00 06  # Chunk length     6
      00 01  # Format           0
      00 01  # Number of tracks 1
      00 78  # Division         120 ticks per quarter-note
"""

_HEADER_TWO_TRACKS = """
4d 54 68 64  # Chunk type       SMF Header ('MThd')
00 00 00 06  # Chunk length     6
      00 01  # Format           1
      00 01  # Number of tracks 2
      00 78  # Division         120 ticks per quarter-note
"""

_ALIEN_CHUNK = """
4d 54 78 78  # Alien chunk:             MTxx
00 00 00 02  # Length of alien data:    2
      00 01  # Alien data
"""


def _parse_hexdump(hexdump):
    data = bytearray()
    for line in hexdump.splitlines():
        data += bytearray.fromhex(line.split('#')[0])
    return data


def _read_file(hexdump, clip=False):
    return MidiFile(file=io.BytesIO(_parse_hexdump(hexdump)), clip=clip)


def test_alien_chunks():
    """Specification page 3 (PDF: 5)

    Your programs should expect alien chunks and treat them as if they
    weren't there.
    """
    with pytest.warns(UserWarning):
        file = _read_file(
            _ALIEN_CHUNK +
            _MINIMAL_SPEC_COMPLIANT_HEADER +
            _MINIMAL_SPEC_COMPLIANT_TRACK
        )
    assert file.format_type == 0
    assert file.division == 96
    assert len(file.tracks) == 1
    assert file.tracks[0] == _DECODED_MINIMAL_SPEC_COMPLIANT_TRACK


def test_first_chunk_not_header():
    """Specifications page 3 (PDF: 5)

    A MIDI file always starts with a header chunk [...]
    """
    with raises(ValueError):
        _read_file(
            _MINIMAL_SPEC_COMPLIANT_TRACK
        )


def test_header_chunk_length_too_small():
    with raises(ValueError):
        _read_file(
            """
            4d 54 68 64  # SMF Header:              MThd
            00 00 00 04  # Length of header data:   4 (instead of the expected 6)
                  00 01  # SMF Format:              1
                  00 00  # Number of tracks:        1
            FF FF FF FF  # Bogus data
            """
            + _MINIMAL_SPEC_COMPLIANT_TRACK
        )


def test_header_chunk_length_too_large():
    with raises(ValueError):
        _read_file(
            """
            4d 54 68 64  # SMF Header:              MThd
            00 00 00 04  # Length of header data:   8 (instead of the expected 6)
                  00 01  # SMF Format:              1
                  00 00  # Number of tracks:        1
                  00 60  # Division                 96 per quarter-note
            FF FF FF FF  # Bogus data
            """
            + _MINIMAL_SPEC_COMPLIANT_TRACK
        )


def test_no_tracks():
    """Specification page 3 (PDF: 5)

    [...] and is followed by one or more track chunks.
    """
    with raises(ValueError):
        _read_file("""
        4d 54 68 64  # MThd
        00 00 00 06  # Chunk size
        00 01  # Type 1
        00 00  # 0 tracks
        00 78  # 120 ticks per beat
        """)


def test_number_track_is_one_for_format_zero():
    """Specification page 4 (PDF: 6)

    [...] the number of track chunks in the file [...] will always be 1 for a
    format 0 file.
    """
    with raises(ValueError):
        _read_file(
            """
            4d 54 68 64  # SMF Header:              MThd
            00 00 00 06  # Length of header data:   6
                  00 00  # SMF Format:              0
                  00 02  # Number of tracks:        2 (Invalid for format 0)
                  00 78  # Division:                120 ticks per quarter-note
            """
            + _MINIMAL_SPEC_COMPLIANT_TRACK
            + _MINIMAL_SPEC_COMPLIANT_TRACK
        )


def test_header_division_metrical_time():
    file = _read_file(
        _MINIMAL_SPEC_COMPLIANT_HEADER +
        _MINIMAL_SPEC_COMPLIANT_TRACK
    )
    assert file.division == 96


def test_header_division_time_code_based_time():
    file = _read_file(
        """
        4d 54 68 64  # SMF Header:              MThd
        00 00 00 06  # Length of header data:   6
              00 00  # SMF Format:              0
              00 01  # Number of tracks:        1
              E2 50  # Division:                bit resolution of 30FPS time code
        """
        + _MINIMAL_SPEC_COMPLIANT_TRACK)
    # FIXME: implement SMPTE time code
    assert file.smpte == -30
    assert file.division == 80


def test_header_unknown_format():
    """Specification page 5 (PDF: 7)

    We may decide to define other format IDs to support other structures.
    A program encountering an unknown format ID may still
    read other MTrk chunks it finds from the file, as format 1 or 2,
    if its user can make sense of them and arrange them into
    some other structure if appropriate
    """
    with pytest.warns(UserWarning):
        file = _read_file(
            """
            4d 54 68 64  # SMF Header:              MThd
            00 00 00 06  # Length of header data:   6
                  00 03  # SMF Format:              3 (Undefined! Only 0, 1 and 2 are defined)
                  00 01  # Number of tracks:        1
                  00 78  # Division:                120 ticks per beat
            """
            + _MINIMAL_SPEC_COMPLIANT_TRACK)
    assert file.format_type == 3
    assert file.division == 120
    assert len(file.tracks) == 1
    assert file.tracks[0] == _DECODED_MINIMAL_SPEC_COMPLIANT_TRACK


def test_header_chunk_extended_length():
    """Specification page 5 (PDF: 7):

    Also, more parameters may be added to the MThd chunk in the future: it is
    important to read and honor the length, even if it is longer than 6.
    """
    with pytest.warns(UserWarning):
        mid = _read_file(
            """
            4d 54 68 64  # SMF Header:              MThd
            00 00 00 08  # Length of header data:   8 (instead of the expected 6)
                  00 01  # SMF Format:              1
                  00 01  # Number of tracks:        1
                  00 78  # Division:                120 ticks per beat
                  99 FF  # Extended header data
            """
            + _MINIMAL_SPEC_COMPLIANT_TRACK)
    assert mid.format_type == 1
    assert mid.division == 120


def test_single_message():
    assert _read_file(_HEADER_ONE_TRACK + """
    4d 54 72 6b  # MTrk
    00 00 00 04
    20 90 40 40  # note_on
    """).tracks[0] == [Message('note_on', note=64, velocity=64, time=32)]


def test_too_long_message():
    with raises(OSError):
        _read_file(_HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 04
        00 ff 03 ff ff 7f # extremely long track name message
        """)


def test_two_tracks():
    mid = _read_file("""
    4d54 6864 0000 0006 0001 0002 0040        # Header
    4d54 726b 0000 0008 00 90 40 10  40 80 40 10   # Track 0
    4d54 726b 0000 0008 00 90 47 10  40 80 47 10   # Track 1
    """)
    assert len(mid.tracks) == 2
    # TODO: add some more tests here.


def test_empty_file():
    with raises(ValueError):
        _read_file("")


def test_eof_in_track():
    with raises(EOFError):
        _read_file(_HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 01  # Chunk size
        # Oops, no data here.
        """)


def test_invalid_data_byte_no_clipping():
    with raises(OSError):
        _read_file(_HEADER_ONE_TRACK + """
        4d 54 72 6b  # MTrk
        00 00 00 04  # Chunk size
        00 90 ff 40  # note_on note=255 velocity=64
        """)


def test_invalid_data_byte_with_clipping_high():
    midi_file = _read_file(_HEADER_ONE_TRACK + """
                          4d 54 72 6b  # MTrk
                          00 00 00 04  # Chunk size
                          00 90 ff 40  # note_on note=255 velocity=64
                          """, clip=True)
    assert midi_file.tracks[0][0].note == 127


def test_meta_messages():
    mid = _read_file(_HEADER_ONE_TRACK + """
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
        _read_file(_HEADER_ONE_TRACK + """
            4d 54 72 6b  # MTrk
            00 00 00 09  # Chunk size
            00 ff 59 02 08 # Key Signature with 8 sharps
            00 ff 2f 00  # end_of_track
            """)


def test_meta_message_bad_key_sig_throws_key_signature_error_flats():
    with raises(KeySignatureError):
        _read_file(_HEADER_ONE_TRACK + """
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
    mid = _read_file(_HEADER_ONE_TRACK + """
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
    midifile = MidiFile(format_type=1, division=123, tracks=[
        MidiTrack([
            Message('note_on', channel=1, note=2, time=3),
            Message('note_off', channel=1, note=2, time=3)]),
        MidiTrack([
            MetaMessage('sequence_number', number=5),
            Message('note_on', channel=2, note=6, time=9),
            Message('note_off', channel=2, note=6, time=9)]),
    ])
    midifile_eval = eval(repr(midifile))
    for track, track_eval in zip(midifile.tracks, midifile_eval.tracks):
        for m1, m2 in zip(track, track_eval):
            assert m1 == m2
