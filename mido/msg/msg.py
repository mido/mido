from .defs import make_msgdict
from .decode import decode_msg, Decoder
from .encode import encode_msg
from .strings import msg2str, str2msg
from .check import check_msgdict


class BaseMessage:
    """Abstrace base class for messages."""
    pass


class Message(BaseMessage):
    def __init__(self, type, **args):
        msgdict = make_msgdict(type, **args)
        check_msgdict(msgdict)
        vars(self).update(msgdict)

    def copy(self, **overrides):
        # Todo: should 'note_on' => 'note_off' be allowed?
        if 'type' in overrides and overrides['type'] != self.type:
            raise ValueError('copy must be same message type')
        
        msgdict = vars(self).copy()
        msgdict.update(overrides)
        check_msgdict(msgdict)
        return Message(**msgdict)

    @classmethod
    def from_bytes(self, data):
        return Message(**decode_msg(data))

    @classmethod
    def from_str(self, text):
        return Message(**str2msg(text))

    @classmethod
    def from_hex(self, text):
        return Message(**decode_msg(bytearray.fromhex(text)))

    def __len__(self):
        # This implementation will cause encode_msg() to be called twice
        # then you iterate over the message. It should instead look up the
        # length in the message definition.
        # 
        # There is no way to get the length of a meta message without
        # encoding it, so we need to either accept double encoding
        # (not good) or leave out __len__() (as Mido 1.1 does).
        return encode_msg(vars(self))

    def __iter__(self):
        yield from encode_msg(vars(self))

    def __str__(self):
        return msg2str(vars(self))

    def __repr__(self):
        return '<message {}>'.format(str(self))

    def __eq__(self, other):
        # This includes time in comparison.
        return vars(self) == vars(other)

    def hex(self, sep=' '):
        return sep.join('{:02X}'.format(byte) for byte in self)


    # This makes the message immutable and allows
    # us to compute a hash.

    def __setattr__(self, name, value):
        raise AttributeError('object is immutable')

    __delattr__ = __setattr__

    def __hash__(self):
        return hash(str(self))


    # These are kept around.

    def bin(self):
        return bytes(self)

    def bytes(self):
        return list(self)

    def bytearray(self):
        return bytearray(self)
