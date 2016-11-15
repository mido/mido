from .frozen import FrozenMetaMessage

def test_meta_init_frozen_args():
    """__init__() can't uses __setattr__() to set attributes."""
    FrozenMetaMessage('track_name', name='Test')
