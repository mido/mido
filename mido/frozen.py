from .messages import Message
from .messages.messages import BaseMessage
from .midifiles import MetaMessage

class Frozen(object):
    is_frozen = True

    def __init__(self, type, **attrs):
        if isinstance(type, BaseMessage):
            vars(self).update(vars(type))
        else:
            super(Frozen, self).__init__(type, **attrs)

    def __repr__(self):
        text = super(Frozen, self).__repr__()
        return '<frozen {}'.format(text[1:])

    def __setattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __delattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __hash__(self):
        return hash(repr(vars(self)))


class FrozenMessage(Frozen, Message):
    pass


class FrozenMetaMessage(Frozen, MetaMessage):
    pass
