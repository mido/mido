import sys
from .specs import make_msgdict, SPEC_BY_TYPE, REALTIME_TYPES
from .check import check_msgdict, check_value, check_data
from .decode import decode_msg, Decoder
from .encode import encode_msg
from .strings import msg2str, str2msg
from ..py2 import convert_py2_bytes


class BaseMessage(object):
    """Abstract base class for messages."""
    is_frozen = False
    is_meta = False

    def copy(self):
        raise NotImplemented

    def bytes(self):
        raise NotImplemented

    def bin(self):
        """Encode message and return as a bytearray.

        This can be used to write the message to a file.
        """
        return bytearray(self.bytes())

    def hex(self, sep=' '):
        """Encode message and return as a string of hex numbers,

        Each number is separated by the string sep.
        """
        return sep.join('{:02X}'.format(byte) for byte in self.bytes())

    @property
    def is_realtime(self):
        return self.type in REALTIME_TYPES

    def __eq__(self, other):
        if not isinstance(other, BaseMessage):
            raise TypeError('comparison between message and another type')

        # This includes time in comparison.
        return vars(self) == vars(other)


class SysexData(tuple):
    """Special kind of tuple accepts and converts any sequence in +=."""
    def __iadd__(self, other):
        check_data(other)
        return self + SysexData(convert_py2_bytes(other))


class Message(BaseMessage):
    def __init__(self, type, **args):
        msgdict = make_msgdict(type, **args)
        check_msgdict(msgdict)
        if type == 'sysex':
            msgdict['data'] = SysexData(convert_py2_bytes(msgdict['data']))
        vars(self).update(msgdict)

    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overridden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.
        """
        if not overrides:
            # Bypass all checks.
            # This will save some time in port.send().
            return self.from_safe_dict(vars(self))

        # Todo: should 'note_on' => 'note_off' be allowed?
        if 'type' in overrides and overrides['type'] != self.type:
            raise ValueError('copy must be same message type')

        msgdict = vars(self).copy()
        msgdict.update(overrides)
        check_msgdict(msgdict)
        return self.__class__(**msgdict)

    @classmethod
    def from_bytes(cl, data, time=0):
        """Parse a byte encoded message.

        It accepts a byte string or any iterable of integers.

        This is the reverse of msg.bytes() or msg.bin().
        """
        return cl(**decode_msg(data, time=time))

    @classmethod
    def from_hex(cl, text, time=0):
        """Parse a hex encoded message.

        This is the reverse of msg.hex().
        """
        return cl(**decode_msg(bytearray.fromhex(text), time=time))

    @classmethod
    def from_str(cl, text):
        """Parse a string encoded message.

        This is the reverse of str(msg).
        """
        return cl(**str2msg(text))

    @classmethod
    def from_safe_bytes(cl, data, time=0):
        """Create a message from bytes without any checks.

        It accepts a byte string or any iterable of integers.

        Use this only when you know the bytes contain a valid message.
        """
        msg = cl.__new__(cl)
        vars(msg).update(decode_msg(data, time=time, check=False))
        return msg

    @classmethod
    def from_safe_dict(cl, msgdict, time=0):
        """Create a message from bytes without name/type/value checks.

        The dictionary should contain the attributes of the new object.
        Use this only when you know the dictionary contains a valid message.
        """
        msg = cl.__new__(cl)
        vars(msg).update(msgdict)
        return msg

    def __len__(self):
        if self.type == 'sysex':
            return 2 + len(self.data)
        else:
            return SPEC_BY_TYPE[self.type]['length']

    def __str__(self):
        return msg2str(vars(self))

    def __repr__(self):
        return '<message {}>'.format(str(self))

    def __setattr__(self, name, value):
        if name == 'type':
            raise AttributeError('type attribute is read only')
        elif name not in vars(self):
            raise AttributeError(
                        '{} message has no attribute {}'.format(self.type, name))
        else:
            check_value(name, value)
            if name == 'data':
                vars(self)['data'] = SysexData(value)
            else:
                vars(self)[name] = value

    def __delattr__(self, name):
        raise AttributeError('attribute cannot be deleted')

    def bytes(self):
        return encode_msg(vars(self))

    def __iter__(self):
        for byte in self.bytes():
            yield byte
    

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
    return msg2str(vars(msg), include_time=include_time)
