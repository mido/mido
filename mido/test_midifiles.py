import io

from .messages import Message
from .midifiles_meta import tempo2bpm, bpm2tempo
from .midifiles import MidiTrack, MetaMessage, MidiFile

MESSAGES = [
    Message('program_change', channel=0, program=12, time=0),
    Message('note_on', channel=0, note=64, velocity=64, time=32),
    Message('note_off', channel=0, note=64, velocity=127, time=128),
    MetaMessage('end_of_track', time=0),
]

EXPECTED_BYTES = (b'MThd\x00\x00\x00\x06\x00\x01\x00\x01\x01\xe0'
                  b'MTrk\x00\x00\x00\x10\x00\xc0\x0c \x90@@\x81\x00\x80@\x7f\x00\xff/\x00')


def compare_tracks(track1, track2):
    """Return True if tracks are equal, otherwise False.

    Ideally track1 == track2 would be enough, but since message comparison
    doesn't include time we need a function for this.
    """
    # Convert to tuples so we compare time.
    track1 = [(msg, msg.time) for msg in track1]
    track2 = [(msg, msg.time) for msg in track2]

    return track1 == track2



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


def test_save_to_bytes():
    mid = MidiFile()
    mid.tracks.append(MidiTrack(MESSAGES))

    bio = io.BytesIO()
    mid.save(file=bio)

    assert bio.getvalue() == EXPECTED_BYTES


def test_load_from_bytes():
    mid = MidiFile(file=io.BytesIO(EXPECTED_BYTES))
    assert compare_tracks(mid.tracks[0], MESSAGES)
