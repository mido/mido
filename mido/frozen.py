from .messages import Message
from .messages.messages import BaseMessage
from .midifiles import MetaMessage

class FrozenMixin(object):
    is_frozen = True

    def __init__(self, type, **attrs):
        if isinstance(type, BaseMessage):
            vars(self).update(vars(type))
        else:
            super(FrozenMixin, self).__init__(type, **attrs)

    def __repr__(self):
        text = super(FrozenMixin, self).__repr__()
        return '<frozen {}'.format(text[1:])

    def __setattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __delattr__(self, *_):
        raise ValueError('frozen message is immutable')

    def __hash__(self):
        return hash(repr(vars(self)))


class FrozenMessage(FrozenMixin, Message):
    pass


class FrozenMetaMessage(FrozenMixin, MetaMessage):
    pass
