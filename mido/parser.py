"""
MIDI Parser

There is no need to use this module directly. All you need is
available in the top level module.
"""

#
# About running status:
#
# http://home.roadrunner.com/~jgglatt/tech/midispec/run.htm
# http://stackoverflow.com/questions/3660964/get-note-data-from-midi-file
#

import sys
from collections import deque
from .messages import Message, build_message, get_spec

PY2 = (sys.version_info.major == 2)


class Parser(object):
    """
    MIDI Parser

    Parses a stream of bytes and produces messages.

    Data can be put into the parser in the form of
    integers, byte arrays or byte strings.
    """

    def __init__(self, data=None):
        """Create a new parser."""
        self.messages = deque()
        self._reset()
        if data is not None:
            self.feed(data)

    def _reset(self):
        self._spec = None
        self._bytes = []
        self._inside_sysex = False

    def _deliver(self, message=None):
        if not message:
            message = build_message(self._spec, self._bytes)
        self.messages.append(message)

    def _handle_status_byte(self, byte):
        try:
            spec = get_spec(byte)
            valid = True
        except LookupError:
            valid = False

        if self._inside_sysex and (0xf8 <= byte <= 0xff):
            # Realtime message inside sysex.
            # Deliver it straight away.
            if valid:
                message = build_message(spec, [byte])
                self._deliver(message)
        elif byte == 0xf7:
            # End of sysex.
            if self._inside_sysex:
                self._deliver()
            self._reset()
        elif valid:
            # Start new message.
            self._spec = spec
            self._bytes = [byte]
            self._inside_sysex = (byte == 0xf0)
        else:
            # Ignore message.
            self._reset()

    def feed_byte(self, byte):
        """Feed one MIDI byte into the parser.

        The byte must be an integer in range 0..255.
        """
        try:
            int(byte)
        except TypeError:
            raise TypeError('byte must be an integer')

        if not 0 <= byte <= 255:
            raise ValueError('byte must be in range 0..255')

        if byte >= 0x80:
            self._handle_status_byte(byte)
        else:
            # Data byte.
            self._bytes.append(byte)

        # If we have a complete messages, deliver it.
        if self._spec and len(self._bytes) == self._spec.length:
            self._deliver()
            self._reset()

    def feed(self, data):
        """Feed MIDI data to the parser.

        Accepts any object that produces a sequence of integers in
        range 0..255, such as:

            [0, 1, 2]
            (0, 1, 2)
            [for i in range(256)]
            (for i in range(256)]
            bytearray()
            b''  # Will be converted to integers in Python 2.
        """
        if PY2 and isinstance(data, str):
            # Byte strings in Python 2 need extra attention.
            for char in data:
                self.feed_byte(ord(char))
        else:
            for byte in data:
                self.feed_byte(byte)

    def pending(self):
        """Return the number of pending messages."""
        return len(self.messages)

    def get_message(self):
        """Get the first parsed message.

        Returns None if there is no message yet. If you don't want to
        deal with None, you can use pending() to see how many messages
        you can get before you get None.
        """
        if self.messages:
            return self.messages.popleft()
        else:
            return None

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self.messages):
            yield self.messages.popleft()


def parse_all(data):
    """Parse MIDI data and return a list of all messages found.

    This is typically used to parse a little bit of data with a few
    messages in it. It's best to use a Parser object for larger
    amounts of data. Also, tt's often easier to use parse() if you
    know there is only one message in the data.
    """
    return list(Parser(data))


def parse(data):
    """ Parse MIDI data and return the first message found.

    Data after the first message is ignored. Use parse_all()
    to parse more than one message.
    """
    return Parser(data).get_message()
