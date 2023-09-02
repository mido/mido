# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import itertools
from mido.file.smf.event.midi import MidiEvent
from mido.file.smf.event.meta import MetaEvent
from mido.file.smf.track import MidiTrack

zip = getattr(itertools, 'izip', zip)


def test_track_slice():
    track = MidiTrack()

    # Slice should return MidiTrack object.
    assert isinstance(track[::], MidiTrack)


def test_track_name():
    name1 = MetaEvent(delta_time=0, type='track_name', name='name1')
    name2 = MetaEvent(delta_time=0, type='track_name', name='name2')

    # The track should use the first name it finds.
    track = MidiTrack([name1, name2])
    assert track.name == name1.name


def test_track_repr():
    track = MidiTrack([
        MidiEvent(delta_time=3, type='note_on', channel=1, note=2),
        MidiEvent(delta_time=3, type='note_off', channel=1, note=2),
    ])
    track_eval = eval(repr(track))
    for m1, m2 in zip(track, track_eval):
        assert m1 == m2
