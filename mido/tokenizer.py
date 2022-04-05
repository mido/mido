from collections import deque
from numbers import Integral
from .messages.specs import (SPEC_BY_STATUS, CHANNEL_MESSAGES, SYSTEM_EXCLUSIVE_MESSAGE, SYSTEM_REALTIME_MESSAGES)


class Tokenizer(object):
    """
    Splits a MIDI byte stream into messages.
    """
    def __init__(self, data=None):
        """Create a new decoder."""

        self._status = 0
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
        if status_byte in SYSTEM_REALTIME_MESSAGES:
            # Directly store message, do not touch statuses and do not end sysex message
            self._messages.append([status_byte])
        else:
            # Any status byte (including EOX) except real time messages ends a sysex message
            if self._status == SYSTEM_EXCLUSIVE_MESSAGE:
                self._status = 0
                self._messages.append(self._bytes)

            # Prepare receiving data bytes if any
            if spec['length'] == 1:
                self._status = 0
                self._messages.append([status_byte])
            else:
                self._status = status_byte
                self._bytes = [status_byte]
                self._len = spec['length']

            # Set or reset running status
            if status_byte in CHANNEL_MESSAGES:
                self._running_status = self._status
            else:  # SYSTEM_COMMON_MESSAGES & SYSTEM_EXCLUSIVE_MESSAGE
                self._running_status = 0

    def _feed_data_byte(self, byte):
        if self._status:
            self._bytes.append(byte)

            if len(self._bytes) == self._len:
                # End complete message
                self._messages.append(self._bytes)

                # Keep current status running if available
                self._bytes = [self._running_status] if self._running_status else []
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
            raise ValueError('invalid byte value {!r}'.format(byte))

    def feed(self, data):
        """Feed MIDI bytes to the decoder.

        Takes an iterable of ints in in range [0..255].
        """
        for byte in data:
            self.feed_byte(byte)

    def __len__(self):
        return len(self._messages)

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self._messages):
            yield self._messages.popleft()
