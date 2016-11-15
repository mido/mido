from .frozen import FrozenMetaMessage, freeze

def test_meta_init_frozen_args():
    """__init__() can't uses __setattr__() to set attributes."""
    FrozenMetaMessage('track_name', name='Test')


def test_freeze_none():
    freeze(None) is None

