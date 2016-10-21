import io

from .messages import Message
from .midifiles import tempo2bpm, bpm2tempo
from .midifiles import MidiTrack, MetaMessage

def test_tempo2bpm_bpm2tempo():
    for bpm, tempo in [
            (20, 3000000),
            (60, 1000000),
            (120, 500000),
            (240, 250000),
    ]:
        assert bpm == tempo2bpm(tempo)
        assert tempo == bpm2tempo(bpm)


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
