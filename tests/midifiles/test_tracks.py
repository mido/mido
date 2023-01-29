import itertools
from mido.messages import Message
from mido.midifiles.meta import MetaMessage
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
    track_eval = eval(repr(track))
    for m1, m2 in zip(track, track_eval):
        assert m1 == m2
