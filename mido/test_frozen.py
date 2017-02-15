from .messages import Message
from .frozen import (is_frozen, freeze_message, thaw_message,
                     FrozenMessage, FrozenMetaMessage, FrozenUnknownMetaMessage)

def test_hashability():
    """Test that messages are hashable."""
    hash(FrozenMessage('note_on'))
    # List is converted to tuple.
    hash(FrozenMessage('sysex', data=[1, 2, 3]))
    hash(FrozenMetaMessage('track_name', name='Some track'))
    hash(FrozenUnknownMetaMessage(123, [1, 2, 3]))


def test_freeze_and_thaw():
    """Test that messages are hashable."""
    assert not is_frozen(thaw_message(freeze_message(Message('note_on'))))


def test_thawed_message_is_copy():
    frozen_msg = FrozenMessage('note_on')
    thawed_msg = Message('note_on')
    assert thaw_message(frozen_msg) == thawed_msg


def test_is_frozen():
    assert is_frozen(FrozenMessage('note_on'))
    assert not is_frozen(Message('note_on'))
