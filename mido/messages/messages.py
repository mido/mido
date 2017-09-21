import re
from .specs import make_msgdict, SPEC_BY_TYPE, REALTIME_TYPES
from .checks import check_msgdict, check_value, check_data
from .decode import decode_message
from .encode import encode_message
from .strings import msg2str, str2msg
from ..py2 import convert_py2_bytes


class BaseMessage(object):
    """Abstract base class for messages."""
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

    def dict(self):
        """Returns a dictionary containing the attributes of the message.

        Example: {'type': 'sysex', 'data': [1, 2], 'time': 0}

        Sysex data will be returned as a list.
        """
        data = vars(self).copy()
        if data['type'] == 'sysex':
            # Make sure we return a list instead of a SysexData object.
            data['data'] = list(data['data'])

        return data

    @classmethod
    def from_dict(cl, data):
        """Create a message from a dictionary.

        Only "type" is required. The other will be set to default
        values.
        """
        return cl(**data)

    @property
    def is_realtime(self):
        """True if the message is a system realtime message."""
        return self.type in REALTIME_TYPES

    def __delattr__(self, name):
        raise AttributeError('attribute cannot be deleted')

    def __setattr__(self, name, value):
        raise AttributeError('message is immutable')

    def __eq__(self, other):
        if not isinstance(other, BaseMessage):
            raise TypeError('can\'t compare message to {}'.format(type(other)))

        # This includes time in comparison.
        return vars(self) == vars(other)


class SysexData(tuple):
    """Special kind of tuple accepts and converts any sequence in +=."""
    def __iadd__(self, other):
        check_data(other)
        return self + SysexData(convert_py2_bytes(other))


class Message(BaseMessage):
    def __init__(self, type, **args):
        msgdict = make_msgdict(type, args)
        if type == 'sysex':
            msgdict['data'] = SysexData(convert_py2_bytes(msgdict['data']))
        check_msgdict(msgdict)
        vars(self).update(msgdict)

    def copy(self, **overrides):
        """Return a copy of the message.

        Attributes will be overridden by the passed keyword arguments.
        Only message specific attributes can be overridden. The message
        type can not be changed.
        """
        if not overrides:
            # Bypass all checks.
            msg = self.__class__.__new__(self.__class__)
            vars(msg).update(vars(self))
            return msg

        if 'type' in overrides and overrides['type'] != self.type:
            raise ValueError('copy must be same message type')

        if 'data' in overrides:
            overrides['data'] = bytearray(overrides['data'])

        msgdict = vars(self).copy()
        msgdict.update(overrides)
        check_msgdict(msgdict)
        return self.__class__(**msgdict)

    @classmethod
    def from_bytes(cl, data, time=0):
        """Parse a byte encoded message.

        Accepts a byte string or any iterable of integers.

        This is the reverse of msg.bytes() or msg.bin().
        """
        msg = cl.__new__(cl)
        msgdict = decode_message(data, time=time)
        if 'data' in msgdict:
            msgdict['data'] = SysexData(msgdict['data'])
        vars(msg).update(msgdict)
        return msg

    @classmethod
    def from_hex(cl, text, time=0, sep=None):
        """Parse a hex encoded message.

        This is the reverse of msg.hex().
        """
        # bytearray.fromhex() is a bit picky about its input
        # so we need to replace all whitespace characters with spaces.
        text = re.sub(r'\s', ' ', text)

        if sep is not None:
            # We also replace the separator with spaces making sure
            # the string length remains the same so char positions will
            # be correct in bytearray.fromhex() error messages.
            text = text.replace(sep, ' ' * len(sep))

        return cl.from_bytes(bytearray.fromhex(text), time=time)

    @classmethod
    def from_str(cl, text):
        """Parse a string encoded message.

        This is the reverse of str(msg).
        """
        return cl(**str2msg(text))

    def __len__(self):
        if self.type == 'sysex':
            return 2 + len(self.data)
        else:
            return SPEC_BY_TYPE[self.type]['length']

    def __str__(self):
        return msg2str(vars(self))

    def __repr__(self):
        return '<message {}>'.format(str(self))

    def _setattr(self, name, value):
        if name == 'type':
            raise AttributeError('type attribute is read only')
        elif name not in vars(self):
            raise AttributeError('{} message has no '
                                 'attribute {}'.format(self.type,
                                                       name))
        else:
            check_value(name, value)
            if name == 'data':
                vars(self)['data'] = SysexData(value)
            else:
                vars(self)[name] = value

    __setattr__ = _setattr

    def bytes(self):
        """Encode message and return as a list of integers."""
        return encode_message(vars(self))


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
