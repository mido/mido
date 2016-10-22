from .specs import make_msgdict, SysexData
from .check import check_msgdict
from .decode import decode_msg, Decoder
from .encode import encode_msg
from .strings import msg2str, str2msg


class BaseMessage:
    """Abstrace base class for messages."""
    pass


class Message(BaseMessage):
    def __init__(self, type, **args):
        msgdict = make_msgdict(type, **args)
        check_msgdict(msgdict)
        if type == 'sysex':
            msgdict['data'] = SysexData(msgdict['data'])
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
    def from_bytes(self, data, time=0):
        return Message(**decode_msg(data, time=time))

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
        check_value(name, value)
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




def parse_string(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    return Message.from_str(text)


def parse_string_stream(stream):
    """Parse a stram of messages and yield (message, error_message)

    stream can be any iterable that generates text strings, where each
    string is a string encoded message.

    If a string can be parsed, (message, None) is returned. If it
    can't be parsed (None, error_message) is returned. The error
    message containes the line number where the error occurred.
    """
    line_number = 1
    for line in stream:
        try:
            line = line.split('#')[0].strip()
            if line:
                yield parse_string(line), None
        except ValueError as exception:
            error_message = 'line {line_number}: {msg}'.format(
                line_number=line_number,
                msg=exception.args[0])
            yield None, error_message
        line_number += 1


def format_as_string(msg, include_time=True):
    """Format a message and return as a string.

    This is equivalent to str(message).

    To leave out the time attribute, pass include_time=False.
    """
    return msg.to_str(include_time=include_time)
