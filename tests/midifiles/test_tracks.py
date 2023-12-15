# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import itertools
import time

import mido
from mido.messages import Message
from mido.midifiles.meta import MetaMessage, UnknownMetaMessage
from mido.midifiles.tracks import MidiTrack

zip = getattr(itertools, 'izip', zip)


def test_track_slice():
    track = MidiTrack()

    # Slice should return MidiTrack object.
    assert isinstance(track[::], MidiTrack)


def test_track_name():
    name1 = MetaMessage('track_name', name='name1')
    name2 = MetaMessage('track_name', name='name2')

    # The track should use the first name it finds.
    track = MidiTrack([name1, name2])
    assert track.name == name1.name


def test_track_repr():
    track = MidiTrack([
        Message('note_on', channel=1, note=2, time=3),
        Message('note_off', channel=1, note=2, time=3),
    ])
    track_eval = eval(repr(track))  # noqa: S307
    for m1, m2 in zip(track, track_eval):
        assert m1 == m2


def test_merge_large_midifile():
    mid = mido.MidiFile()
    for k in range(5):
        t = mido.MidiTrack()
        for _ in range(10000):
            t.append(mido.Message("note_on", note=72, time=1000 + 100 * k))
            t.append(mido.Message("note_off", note=72, time=500 + 100 * k))
        mid.tracks.append(t)

    # Add meta messages for testing.
    meta1 = mido.MetaMessage('track_name', name='Test Track 1')
    meta2 = mido.MetaMessage('track_name', name='Test Track 2')
    meta3 = mido.MetaMessage('time_signature',
                             numerator=4,
                             denominator=4,
                             clocks_per_click=24,
                             notated_32nd_notes_per_beat=8)
    unknown_meta = mido.UnknownMetaMessage(0x50, b'\x01\x02\x03')

    mid.tracks[0].insert(0, meta1)
    mid.tracks[1].insert(0, meta2)
    mid.tracks[2].insert(0, meta3)
    mid.tracks[3].insert(0, unknown_meta)

    start = time.time()
    merged = list(mido.merge_tracks(mid.tracks, skip_checks=True))
    finish = time.time()

    merged_duration_ticks = sum(msg.time for msg in merged)
    max_track_duration_ticks = max(
        sum(msg.time for msg in t) for t in mid.tracks)
    assert merged_duration_ticks == max_track_duration_ticks
    assert (finish - start) < 3.0
