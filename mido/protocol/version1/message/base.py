# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDI 1.0 Protocol Messages Base
"""

from .specs import REALTIME_TYPES, SPEC_BY_TYPE


class BaseMessage:
    """Abstract base class for messages."""
    is_meta = False

    @property
    def is_realtime(self):
        """True if the message is a system realtime message."""
        return self.type in REALTIME_TYPES

    @classmethod
    def from_dict(cls, data):
        """Create a message from a dictionary.

        Only "type" is required. The other will be set to default
        values.
        """
        return cls(**data)

    def __repr__(self):
        items = [repr(self.type)]
        for name in self._get_value_names():
            items.append(f'{name}={getattr(self, name)!r}')
        return '{}({})'.format(type(self).__name__, ', '.join(items))

    def __delattr__(self, name):
        raise AttributeError('attribute cannot be deleted')

    def __setattr__(self, name, value):
        raise AttributeError('message is immutable')

    def __eq__(self, other):
        if not isinstance(other, BaseMessage):
            raise TypeError(f'can\'t compare message to {type(other)}')

        # This includes timestamp and delta_time in comparison.
        return vars(self) == vars(other)

    def _get_value_names(self):
        # This is overridden by MetaEvent.
        return list(SPEC_BY_TYPE[self.type]['value_names']) + ['timestamp']

    def bytes(self):
        raise NotImplementedError

    def bin(self):
        """Encode message and return as a bytearray.

        This can be used to write the message to a file.
        """
        return bytearray(self.bytes())

    def copy(self):
        raise NotImplementedError

    def dict(self):
        """Returns a dictionary containing the attributes of the message.

        Example: {'type': 'sysex', 'data': [1, 2], 'timestamp': 0}

        Sysex data will be returned as a list.
        """
        data = vars(self).copy()
        if data['type'] == 'sysex':
            # Make sure we return a list instead of a SysexData object.
            data['data'] = list(data['data'])

        return data

    def hex(self, sep=' '):
        """Encode message and return as a string of hex numbers,

        Each number is separated by the string sep.
        """
        return sep.join(f'{byte:02X}' for byte in self.bytes())

    def is_cc(self, control=None):
        """Return True if the message is of type 'control_change'.

        The optional control argument can be used to test for a specific
        control number, for example:

        if msg.is_cc(7):
            # Message is control change 7 (channel volume).
        """
        if self.type != 'control_change':
            return False
        elif control is None:
            return True
        else:
            return self.control == control
