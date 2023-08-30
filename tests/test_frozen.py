# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from mido.protocol.version1.message import Message
from mido.file.smf.meta import UnknownMetaEvent
from mido.protocol.version1.message.frozen import (
    is_frozen, freeze_message, thaw_message,
    FrozenMessage, FrozenMetaEvent, FrozenUnknownMetaEvent)


def test_hashability():
    """Test that messages are hashable."""
    hash(FrozenMessage('note_on'))
    # List is converted to tuple.
    hash(FrozenMessage('sysex', data=[1, 2, 3]))
    hash(FrozenMetaEvent('track_name', name='Some track'))
    hash(FrozenUnknownMetaEvent(123, [1, 2, 3]))


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


def test_frozen_repr():
    msg = FrozenMessage('note_on', channel=1, note=2, time=3)
    msg_eval = eval(repr(msg))
    assert isinstance(msg_eval, FrozenMessage)
    assert msg == msg_eval


def test_frozen_meta_repr():
    msg = FrozenMetaEvent('end_of_track', time=10)
    msg_eval = eval(repr(msg))
    assert isinstance(msg_eval, FrozenMetaEvent)
    assert msg == msg_eval


def test_frozen_unknown_meta_repr():
    msg = FrozenUnknownMetaEvent(type_byte=99, data=[1, 2], time=10)
    msg_eval = eval(repr(msg))
    assert isinstance(msg_eval, UnknownMetaEvent)
    assert msg == msg_eval
