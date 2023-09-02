# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Standard MIDI File (SMF) MIDI (Message) Events
"""

import re

from mido.protocol.version1.message.checks import check_time
from mido.protocol.version1.message.decode import decode_message
from mido.protocol.version1.message.message import Message, SysexData
from mido.protocol.version1.message.specs import SPEC_BY_TYPE
from mido.protocol.version1.message.strings import msg2str
from .base import MtrkEvent


class MidiEvent(MtrkEvent, Message):
    @classmethod
    def from_bytes(cls, data, delta_time=0):
        """Parse a byte encoded message event.

        Accepts a byte string or any iterable of integers.

        This is the reverse of msg.bytes() or msg.bin().
        """
        msg = cls.__new__(cls)
        msgdict = decode_message(data, timestamp=0, delta_time=delta_time)
        if 'data' in msgdict:
            msgdict['data'] = SysexData(msgdict['data'])
        vars(msg).update(msgdict)
        return msg

    @classmethod
    def from_hex(cls, text, delta_time=0, sep=None):
        """Parse a hex encoded message event.

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

        return cls.from_bytes(bytearray.fromhex(text), delta_time=delta_time)

    def __init__(self, type, delta_time, **args):
        super().__init__(type, **args)
        check_time(delta_time)
        self.delta_time = delta_time
        if self.is_realtime:
            raise ValueError('Events cannot be realtime messages')

    def __str__(self):
        return msg2str(vars(self), include_delta_time=True)

    def _get_value_names(self):
        # This is overridden by MetaEvent.
        return list(SPEC_BY_TYPE[self.type]['value_names']) + ['delta_time']
