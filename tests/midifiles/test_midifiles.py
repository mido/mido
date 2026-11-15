# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import io

from pytest import raises

from mido.messages import Message
from mido.midifiles.meta import KeySignatureError, MetaMessage
from mido.midifiles.midifiles import MidiFile, MidiTrack, ParseError

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


def test_midifile_invalid_type_error_message():
    # https://github.com/mido/mido/issues/673
    # the error used to interpolate the builtin format function instead of
    # the value that was rejected
    with raises(ValueError) as e:
        MidiFile(type=3)
    assert 'invalid format 3 (must be 0, 1 or 2)' in str(e.value)


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


# Hardened (opt-in) parse mode.
#
# Each malformed input below crashes the default parser with a different
# low-level exception. With hardened=True that exception must be collapsed
# into a single mido.ParseError; with the default hardened=False the
# original exception and all other behaviour must be unchanged.

# ticks_per_beat = 0 -> ZeroDivisionError in the tick/second conversion
# while iterating.
HARDENED_TICKS_PER_BEAT_ZERO = """
4d 54 68 64  # MThd
00 00 00 06
      00 01  # type 1
      00 01  # 1 track
      00 00  # 0 ticks per beat
4d 54 72 6b  # MTrk
00 00 00 04
20 90 40 40  # note_on, delta 32
"""

# set_tempo meta declares length 1 but decode indexes data[1], data[2]
# -> IndexError.
HARDENED_TRUNCATED_SET_TEMPO = HEADER_ONE_TRACK + """
4d 54 72 6b
00 00 00 05
00 ff 51 01 07  # set_tempo, declared length 1
"""

# smpte_offset with frame_rate bits (data[0] >> 5) == 7, not in the
# lookup table -> KeyError.
HARDENED_BAD_SMPTE = HEADER_ONE_TRACK + """
4d 54 72 6b
00 00 00 09
00 ff 54 05 e0 00 00 00 00  # smpte_offset, bad frame_rate bits
"""

# Meta message declares more payload bytes than the stream holds
# -> EOFError.
HARDENED_TRUNCATED_STREAM = HEADER_ONE_TRACK + """
4d 54 72 6b
00 00 00 05
00 ff 51 03 07  # set_tempo declares length 3, stream ends early
"""

# A type 2 (asynchronous) file cannot merge its tracks; iterating it
# raises TypeError.
HARDENED_TYPE_2 = """
4d 54 68 64
00 00 00 06
      00 02  # type 2
      00 01
      00 78
4d 54 72 6b
00 00 00 04
20 90 40 40
"""

HARDENED_CASES = [
    (HARDENED_TICKS_PER_BEAT_ZERO, ZeroDivisionError),
    (HARDENED_TRUNCATED_SET_TEMPO, IndexError),
    (HARDENED_BAD_SMPTE, KeyError),
    (HARDENED_TRUNCATED_STREAM, EOFError),
    (HARDENED_TYPE_2, TypeError),
]


def _consume(hexdump, hardened):
    # list() forces both the load-time and the iterate-time parse paths.
    return list(MidiFile(file=io.BytesIO(parse_hexdump(hexdump)),
                         hardened=hardened))


def test_hardened_defaults_to_off():
    assert MidiFile(type=1).hardened is False


def test_hardened_off_keeps_original_exceptions():
    for hexdump, exc_type in HARDENED_CASES:
        with raises(exc_type):
            _consume(hexdump, hardened=False)


def test_hardened_on_collapses_into_parse_error():
    for hexdump, exc_type in HARDENED_CASES:
        with raises(ParseError) as excinfo:
            _consume(hexdump, hardened=True)
        # The original exception is preserved as the cause.
        assert isinstance(excinfo.value.__cause__, exc_type)


def test_hardened_on_does_not_change_valid_file():
    # A well-formed file parses and iterates identically with hardened on.
    plain = read_file(HEADER_ONE_TRACK + """
    4d 54 72 6b
    00 00 00 04
    20 90 40 40  # note_on
    """)
    hardened = MidiFile(
        file=io.BytesIO(parse_hexdump(HEADER_ONE_TRACK + """
        4d 54 72 6b
        00 00 00 04
        20 90 40 40  # note_on
        """)),
        hardened=True,
    )
    assert hardened.hardened is True
    assert hardened.tracks == plain.tracks
    assert list(hardened) == list(plain)


def test_hardened_leaves_deliberate_oserror_alone():
    # mido raises OSError on purpose for a missing MThd header. Hardened
    # mode must not swallow that into ParseError.
    not_a_midi = "00 00 00 00 00 00 00 00"
    with raises(OSError):
        MidiFile(file=io.BytesIO(parse_hexdump(not_a_midi)), hardened=True)
