from .messages import Message
from .messages.messages import BaseMessage
from .midifiles import MetaMessage, UnknownMetaMessage

class Frozen(object):
    def __repr__(self):
        text = super(Frozen, self).__repr__()
        return '<frozen {}'.format(text[1:])

    def __setattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __delattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __hash__(self):
        return hash(tuple(sorted(vars(self).items())))


class FrozenMessage(Frozen, Message):
    pass


class FrozenMetaMessage(Frozen, MetaMessage):
    pass


class FrozenUnknownMetaMessage(Frozen, UnknownMetaMessage):
    pass


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
    elif isinstance(msg, UnknownMetaMessage):
        class_ = FrozenUnknownMetaMessage
    elif isinstance(msg, MetaMessage):
        class_ = FrozenMetaMessage
    elif msg is None:
        return None
    else:
        raise ValueError('first argument must be a message or None')

    frozen = class_.__new__(class_)
    vars(frozen).update(vars(msg))
    return frozen
