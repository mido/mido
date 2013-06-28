"""
MIDI Parser

Module content:

    Parser()
        feed(data)
        feed_byte(byte)
        pending()      return the number of pending messages
        get_message() -> Message or None
        __iter__()    iterate through available messages

    parse(data) -> Message or None
    parse_all(data) -> [Message, ...]

byte is an integer in range 0 .. 255.
data is any sequence of bytes, or an object that generates them.
"""

import sys
from collections import deque
from .messages import Message, MIN_PITCHWHEEL

python2 = (sys.version_info.major == 2)


class Parser(object):
    """
    MIDI Parser

    Parses a stream of bytes and produces messages.

    Data can be put into the parser in the form of
    integers, bytearrays or byte strings.
    """

    def __init__(self):
        """Create a new parser."""
        self._parsed_messages = deque()
        self._current_message = None
        self._data_bytes = []  # Data bytes

    def _deliver_message(self, message):
        """Deliver message into message deque and reset internal
        state for next message.
        """
        self._parsed_messages.append(message)
        self._current_message = None
        self._data_bytes = []

    def feed_byte(self, byte):
        """Feed one MIDI byte into the parser.

        The byte must be an integer in range 0 .. 255.
        """
        try:
            int(byte)
        except TypeError:
            raise TypeError('byte must be an integer (was {!r})'.format(byte))

        if not 0 <= byte <= 255:
            raise ValueError('byte out of range: {!r}'.format(byte))

        #
        # Handle byte
        #
        if byte >= 0x80:
            # New message
            status_byte = byte

            if 0xf8 <= status_byte <= 0xff:
                # Realtime message.

                # Are we inside a sysex message?
                if (self._current_message and
                    self._current_message.type == 'sysex'):
                    # Realtime messages are allowed inside sysex.
                    # We append directly to _messages so we don't
                    # lose the sysex message.
                    self._parsed_messages.append(Message(status_byte))
                else:
                    self._deliver_message(Message(status_byte))

            elif status_byte == 0xf7:
                # End of sysex
                if self._current_message:
                    self._current_message.data = self._data_bytes
                    self._deliver_message(self._current_message)
                else:
                    pass  # Stray sysex_end byte. Ignore it.
            else:
                # Start a new message.
                self._current_message = Message(status_byte)
        else:
            # Data byte.
            if self._current_message:
                self._data_bytes.append(byte)
                
                # Do we have enough data bytes for a complete message?
                data_size = self._current_message.spec.size - 1
                if len(self._data_bytes) == data_size:
                    self._add_data_bytes(self._current_message,
                                         self._data_bytes)
                    self._deliver_message(self._current_message)

    def _add_data_bytes(self, message, data_bytes):
        """Add data bytes that we have collected to the message.

        For internal use.
        """

        if message.type == 'sysex':
            message.data = data

        elif message.type == 'pitchwheel':
            message.pitch = (data_bytes[0] | (data_bytes[1] << 7)) \
                + MIN_PITCHWHEEL

        elif message.type == 'songpos':
            value = data_bytes[0] | data_bytes[1] << 7
            message.pos = value

        else:
            if hasattr(message, 'channel'):
                # Skip channel. It's already masked into the status byte.
                attribute_names = message.spec.args[1:]
            else:
                attribute_names = message.sped.args

            # The remaining arguments are all one data byte each.
            # Map them to attributes.
            for (name, value) in zip(attribute_names, data_bytes):
                setattr(message, name, value)

    def feed(self, data):
        """Feed MIDI data to the parser.

        Accepts any object that produces a sequence of integers in
        range 0 .. 255, such as:

            [0, 1, 2]
            (0, 1, 2)
            [for i in range(256)]
            (for i in range(256)]
            bytearray()
            b''  # Will be converted to integers in Python 2.
        """
        if python2 and isinstance(data, str):
            # Byte strings in Python 2 need extra attention.
            for char in data:
                self.feed_byte(ord(char))
        else:
            for byte in data:
                self.feed_byte(byte)

    def pending(self):
        """Return the number of pending messages."""
        return len(self._parsed_messages)

    def get_message(self):
        """Get the first parsed message.

        Returns None if there is no message yet. If you don't want to
        deal with None, you can use pending() to see how many messages
        you can get before you get None.
        """
        if self._parsed_messages:
            return self._parsed_messages.popleft()
        else:
            return None

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        while len(self._parsed_messages):
            yield self._parsed_messages.popleft()


def parse_all(data):
    """Parse MIDI data and return a list of all messages found.

    This is typically used to parse a little bit of data with a few
    messages in it. It's best to use a Parser object for larger
    amounts of data. Also, tt's often easier to use parse() if you
    know there is only one message in the data.
    """
    parser = Parser()
    parser.feed(data)
    return list(parser)


def parse(data):
    """ Parse MIDI data and return the first message found.

    Data after the first message is ignored. Use parse_all()
    to parse more than one message.
    """
    parser = Parser()
    parser.feed(data)
    return parser.get_message()
