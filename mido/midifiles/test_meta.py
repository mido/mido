from pytest import raises
from .meta import MetaMessage

def test_copy_invalid_argument():
    with raises(ValueError):
        MetaMessage('track_name').copy(a=1)


def test_copy_cant_override_type():
    with raises(ValueError):
        MetaMessage('track_name').copy(type='end_of_track')
