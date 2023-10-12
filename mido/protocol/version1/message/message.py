# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDI 1.0 Protocol Messages
"""

import re
import warnings

from .base import BaseMessage
from .checks import check_msgdict, check_value, check_data
from .decode import decode_message
from .encode import encode_message
from .specs import make_msgdict, SPEC_BY_TYPE
from .strings import msg2str, str2msg


class SysexData(tuple):
    """Special kind of tuple accepts and converts any sequence in +=."""
    def __iadd__(self, other):
        check_data(other)
        return self + SysexData(other)


class Message(BaseMessage):
    type: str
    data: list
    timestamp: int
    delta_time: int

    @classmethod
    def from_bytes(cls, data, timestamp=0):
        """Parse a byte encoded message.

        Accepts a byte string or any iterable of integers.

        This is the reverse of msg.bytes() or msg.bin().
        """
        msg = cls.__new__(cls)
        msgdict = decode_message(data, timestamp=timestamp)
        if 'data' in msgdict:
            msgdict['data'] = SysexData(msgdict['data'])
        vars(msg).update(msgdict)
        return msg

    @classmethod
    def from_hex(cls, text, timestamp=0, sep=None):
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

        return cls.from_bytes(bytearray.fromhex(text), timestamp=timestamp)

    @classmethod
    def from_str(cls, text):
        """Parse a string encoded message.

        This is the reverse of str(msg).
        """
        return cls(**str2msg(text))

    @property
    def time(self):
        warnings.warn("time is deprecated in favor of "
                      "timestamp or delta_time.",
                      DeprecationWarning,
                      stacklevel=2)
        return self.timestamp

    def __init__(self, type, **args):
        msgdict = make_msgdict(type, args)
        if type == 'sysex':
            msgdict['data'] = SysexData(msgdict['data'])
        check_msgdict(msgdict)
        vars(self).update(msgdict)

    def __len__(self):
        if self.type == 'sysex':
            return 2 + len(self.data)
        else:
            return SPEC_BY_TYPE[self.type]['length']

    def __str__(self):
        return msg2str(vars(self), include_timestamp=True)

    def _setattr(self, name, value):
        if name == 'time':
            warnings.warn(
                "time is deprecated in favor of "
                "timestamp or delta_time.",
                DeprecationWarning,
                stacklevel=2,
            )
            check_value('timestamp', value)
            vars(self)['timestamp'] = value
            return
        if name == 'type':
            raise AttributeError('type attribute is read only')
        if name == 'timestamp' or name == 'delta_time':
            check_value(name, value)
            vars(self)[name] = value
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


def parse_string(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    return Message.from_str(text)


def parse_string_stream(stream):
    """Parse a stream of messages and yield (message, error_message)

    stream can be any iterable that generates text strings, where each
    string is a string encoded message.

    If a string can be parsed, (message, None) is returned. If it
    can't be parsed, (None, error_message) is returned. The error
    message contains the line number where the error occurred.
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


def format_as_string(msg, include_timestamp=True, include_delta_time=True):
    """Format a message and return as a string.

    This is equivalent to str(message).

    To leave out the time attribute, pass include_timestamp=False.
    """
    return msg2str(vars(msg),
                   include_timestamp=include_timestamp,
                   include_delta_time=include_delta_time)
