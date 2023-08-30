# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from mido.protocol.version1.message import Message
from mido.file.smf import MetaEvent, UnknownMetaEvent


class Frozen:
    def __setattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __hash__(self):
        return hash(tuple(sorted(vars(self).items())))


class FrozenMessage(Frozen, Message):
    pass


class FrozenMetaEvent(Frozen, MetaEvent):
    pass


class FrozenUnknownMetaEvent(Frozen, UnknownMetaEvent):
    def __repr__(self):
        return 'Frozen' + UnknownMetaEvent.__repr__(self)


def is_frozen(msg):
    """Return True if message is frozen, otherwise False."""
    return isinstance(msg, Frozen)


# TODO: these two functions are almost the same except inverted. There
# should be a way to refactor them to lessen code duplication.

def freeze_message(msg):
    """Freeze message.

    Returns a frozen version of the message. Frozen messages are
    immutable, hashable and can be used as dictionary keys.

    Will return None if called with None. This allows you to do things
    like::

        msg = freeze_message(port.poll())
    """
    if isinstance(msg, Frozen):
        # Already frozen.
        return msg
    elif isinstance(msg, Message):
        class_ = FrozenMessage
    elif isinstance(msg, UnknownMetaEvent):
        class_ = FrozenUnknownMetaEvent
    elif isinstance(msg, MetaEvent):
        class_ = FrozenMetaEvent
    elif msg is None:
        return None
    else:
        raise ValueError('first argument must be a message or None')

    frozen = class_.__new__(class_)
    vars(frozen).update(vars(msg))
    return frozen


def thaw_message(msg):
    """Thaw message.

    Returns a mutable version of a frozen message.

    Will return None if called with None.
    """
    if not isinstance(msg, Frozen):
        # Already thawed, just return a copy.
        return msg.copy()
    elif isinstance(msg, FrozenMessage):
        class_ = Message
    elif isinstance(msg, FrozenUnknownMetaEvent):
        class_ = UnknownMetaEvent
    elif isinstance(msg, FrozenMetaEvent):
        class_ = MetaEvent
    elif msg is None:
        return None
    else:
        raise ValueError('first argument must be a message or None')

    thawed = class_.__new__(class_)
    vars(thawed).update(vars(msg))
    return thawed
