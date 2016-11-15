from pytest import raises
from .meta import tempo2bpm, bpm2tempo, MetaMessage

def test_tempo2bpm_bpm2tempo():
    for bpm, tempo in [
            (20, 3000000),
            (60, 1000000),
            (120, 500000),
            (240, 250000),
    ]:
        assert bpm == tempo2bpm(tempo)
        assert tempo == bpm2tempo(bpm)


def test_copy_invalid_argument():
    with raises(ValueError):
        MetaMessage('track_name').copy(a=1)


def test_copy_cant_override_type():
    with raises(ValueError):
        MetaMessage('track_name').copy(type='end_of_track')
