from .frozen import FrozenMessage
from .frozen import FrozenMetaMessage, FrozenUnknownMetaMessage

def test_hashability():
    """Test that messages are hashable."""
    hash(FrozenMessage('note_on'))
    # List is converted to tuple.
    hash(FrozenMessage('sysex', data=[1, 2, 3]))
    hash(FrozenMetaMessage('track_name', name='Some track'))
    hash(FrozenUnknownMetaMessage(123, [1, 2, 3]))


