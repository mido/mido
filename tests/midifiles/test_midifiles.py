# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import io

from pytest import approx, fixture, mark, raises

from mido.messages import Message
from mido.midifiles import midifiles
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


class PlaybackClock:
    def __init__(self):
        self.time = 100.0
        self.sleeps = []

    def now(self):
        return self.time

    def sleep(self, duration):
        self.sleeps.append(duration)
        self.time += duration


@fixture
def playback_clock(monkeypatch):
    clock = PlaybackClock()
    monkeypatch.setattr(midifiles.time, 'sleep', clock.sleep)
    return clock


@mark.parametrize('cached', [False, True])
@mark.parametrize('first_ticks', [0, 480])
def test_play_excludes_merge_time(
    monkeypatch, playback_clock, cached, first_ticks,
):
    merge_tracks = midifiles.merge_tracks
    merge_calls = []

    def slow_merge(*args, **kwargs):
        merge_calls.append(playback_clock.now())
        playback_clock.time += 2.0
        return merge_tracks(*args, **kwargs)

    monkeypatch.setattr(midifiles, 'merge_tracks', slow_merge)
    mid = MidiFile(ticks_per_beat=480, tracks=[
        MidiTrack([Message('note_on', note=60, time=first_ticks)]),
        MidiTrack([Message('note_on', note=64, time=first_ticks + 480)]),
    ])
    assert merge_calls == []
    if cached:
        _ = mid.merged_track
    player = mid.play(now=playback_clock.now)
    assert len(merge_calls) == int(cached)

    # Waiting before advancing the generator must not consume MIDI time.
    playback_clock.time += 3.0
    first_delay = first_ticks / 960.0
    messages = []
    times = []
    for msg in player:
        messages.append(msg)
        times.append(playback_clock.now())

    assert len(merge_calls) == 1
    assert messages == [
        Message('note_on', note=60, time=first_delay),
        Message('note_on', note=64, time=0.5),
    ]
    assert times == approx([105.0 + first_delay, 105.5 + first_delay])
    expected_sleeps = [first_delay, 0.5] if first_ticks else [0.5]
    assert playback_clock.sleeps == approx(expected_sleeps)


@mark.parametrize('meta_messages', [False, True])
def test_play_tempo_and_meta_messages(playback_clock, meta_messages):
    mid = MidiFile(ticks_per_beat=480, tracks=[MidiTrack([
        MetaMessage('track_name', name='Test', time=480),
        MetaMessage('set_tempo', tempo=1000000, time=480),
        Message('note_on', note=60, time=480),
        Message('note_off', note=60, time=480),
        MetaMessage('end_of_track', time=240),
    ])])
    messages = []
    times = []
    for msg in mid.play(meta_messages=meta_messages, now=playback_clock.now):
        messages.append(msg)
        times.append(playback_clock.now())

    expected = [
        Message('note_on', note=60, time=1.0),
        Message('note_off', note=60, time=1.0),
    ]
    expected_times = [102.0, 103.0]
    if meta_messages:
        expected = [
            MetaMessage('track_name', name='Test', time=0.5),
            MetaMessage('set_tempo', tempo=1000000, time=0.5),
        ] + expected + [MetaMessage('end_of_track', time=0.5)]
        expected_times = [100.5, 101.0, 102.0, 103.0, 103.5]
    assert messages == expected
    assert times == approx(expected_times)
    assert playback_clock.sleeps == approx([0.5, 0.5, 1.0, 1.0, 0.5])
    assert playback_clock.now() == approx(103.5)


@mark.parametrize('consumer_delay', [0.25, 0.75])
def test_play_compensates_for_consumer_delay(playback_clock, consumer_delay):
    mid = MidiFile(ticks_per_beat=480, tracks=[MidiTrack([
        Message('note_on', note=60, time=480),
        Message('note_on', note=62, time=480),
        Message('note_on', note=64, time=480),
    ])])
    player = mid.play(now=playback_clock.now)
    assert next(player) == Message('note_on', note=60, time=0.5)
    assert playback_clock.now() == approx(100.5)
    playback_clock.time += consumer_delay
    assert next(player) == Message('note_on', note=62, time=0.5)
    assert playback_clock.now() == approx(max(101.0, 100.5 + consumer_delay))
    assert next(player) == Message('note_on', note=64, time=0.5)
    assert playback_clock.now() == approx(101.5)
    assert list(player) == []
    expected_sleeps = ([0.5, 0.25, 0.5] if consumer_delay == 0.25
                       else [0.5, 0.25])
    assert playback_clock.sleeps == approx(expected_sleeps)


@mark.parametrize('tracks', [[], [MidiTrack()]])
@mark.parametrize('meta_messages', [False, True])
def test_play_empty(playback_clock, tracks, meta_messages):
    mid = MidiFile(tracks=tracks)
    player = mid.play(meta_messages=meta_messages, now=playback_clock.now)
    assert list(player) == (
        [MetaMessage('end_of_track')] if meta_messages else [])
    assert playback_clock.sleeps == []


def test_play_type_2(playback_clock):
    mid = MidiFile(type=2)
    with raises(TypeError, match="can't merge tracks in type 2"):
        list(mid.play(now=playback_clock.now))
    assert playback_clock.sleeps == []
