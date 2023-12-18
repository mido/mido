# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDI 1.0 Byte-Stream Tokenizer
"""
import warnings
from collections import deque
from numbers import Integral

from mido.protocol.version1.message.specs import (
    CHANNEL_MESSAGES,
    REALTIME_MESSAGES,
    SPEC_BY_STATUS,
    SYSEX_END,
    SYSEX_START,
)


class Tokenizer:
    """
    Splits a MIDI byte stream into messages.
    """
    def __init__(self, data=None):
        """Create a new decoder."""

        self._current_status = 0
        self._running_status = 0
        self._bytes = []
        self._messages = deque()
        self._datalen = 0

        if data is not None:
            self.feed(data)

    def _feed_status_byte(self, status_byte):
        # Data validation
        try:
            spec = SPEC_BY_STATUS[status_byte]
        except KeyError:
            # Invalid status byte: ignore
            return

        # New message processing
        if status_byte in REALTIME_MESSAGES:
            # Directly store message,
            # do not touch statuses and do not end sysex message
            self._messages.append([status_byte])
            return

        # Any status byte (including EOX) except real time messages
        # ends a sysex message
        if self._current_status == SYSEX_START:
            self._current_status = 0
            self._messages.append(self._bytes)
            if status_byte == SYSEX_END:
                # FIXME: end_of_exclusive should be a separate message
                # Let's keep compatible behavior for now.
                self._bytes.append(status_byte)
                return

        # Prepare receiving data bytes if any
        if spec['length'] == 1:
            self._current_status = 0
            self._messages.append([status_byte])
        else:
            self._current_status = status_byte
            self._bytes = [status_byte]
            self._len = spec['length']

        # Set or reset running status
        if status_byte in CHANNEL_MESSAGES:
            self._running_status = self._current_status
        else:  # SYSTEM_COMMON_MESSAGES & SYSTEM_EXCLUSIVE_MESSAGE
            self._running_status = 0

    def _feed_data_byte(self, byte):
        if self._current_status:
            self._bytes.append(byte)

            if len(self._bytes) == self._len:
                # End complete message
                self._messages.append(self._bytes)

                # Keep current status running if available
                if self._running_status:
                    self._bytes = [self._running_status]
                else:
                    self._current_status = 0
        else:
            # Ignore stray data byte.
            pass

    def feed_byte(self, byte):
        """Feed MIDI byte to the decoder.

        Takes an int in range [0..255].
        """
        if not isinstance(byte, Integral):
            raise TypeError('message byte must be integer')

        if 0 <= byte <= 255:
            if byte > 127:
                return self._feed_status_byte(byte)
            else:
                return self._feed_data_byte(byte)
        else:
            raise ValueError(f'invalid byte value {byte!r}')

    def feed(self, data):
        """Feed MIDI bytes to the decoder.

        Takes an iterable of ints in range [0..255].
        """
        for byte in data:
            self.feed_byte(byte)

    def __len__(self):
        return len(self._messages)

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self._messages):
            yield self._messages.popleft()
