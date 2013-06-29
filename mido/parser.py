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
        self._status_byte = None
        self._data_bytes = []  # Data bytes
        self._bytes_to_go = None

    def _build_message(self):
        type_ = self._spec.type

        if type_ == 'sysex':
            return Message('sysex', data=data)

        elif type_ == 'pitchwheel':
            pitch = self._data_bytes[0] | \
                ((self._data_bytes[1] << 7) + MIN_PITCHWHEEL)
            m = Message('pitchwheel', pitch=pitch)
            return m

        elif type_ == 'songpos':
            return Message('songpos', pos=(self._data_bytes[0] | \
                                               (self._data_bytes[1] << 7)))

        else:
            if self._status_byte < 0xf0:
                attribute_names = self._spec.arguments[1:]
            else:
                attribute_names = self._spec.arguments

            return Message(type_, **dict(zip(attribute_names, self._data_bytes)))

    def _handle_status_byte(self, byte):
        if 0xf8 <= byte <= 0xff:
            # Realtime message are delivered straight away.
            self._parsed_messages.append(Message(byte))

            if self._status_byte != 0xf0:
                # Realtime message arrived inside a non-sysex
                # message. Discard the message we were parsing.
                self._status_byte = None

        elif byte == 0xf7:
            # End of sysex
            if self._status_byte == 0xf0:
                # We were inside a sysex message. Deliver it.
                self._parsed_messages.append(Message('sysex',
                                                     data=self._data_bytes))
                self._status_byte = None
            else:
                # Ignore stray end_of_sysex.
                pass
        else:
            # Start of new message
            self._status_byte = byte
            self._spec = Message._spec_lookup[byte]
            self._bytes_to_go = self._spec.size - 1

    def _handle_data_byte(self, byte):
        self._data_bytes.append(byte)

        if self._status_byte:
            self._bytes_to_go -= 1
            if self._bytes_to_go == 0:
                self._parsed_messages.append(self._build_message())
        else:
            # Stray data byte. Ignore it.
            pass

    def feed_byte(self, byte):
        """Feed one MIDI byte into the parser.

        The byte must be an integer in range 0 .. 255.
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
            self._handle_data_byte(byte)

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
