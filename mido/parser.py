"""
MIDI Parser

The API may change to make it more streamlined. This class should be
considered internal to Mido for now.

    Parser()
        put_byte(byte)
        feed(data)
        get_msg() -> Message or None
        reset()
        messages

    parse(data) -> Message or None
    parseall(data) -> [Message, ...]

byte is an integer in range 0 - 255.
data is any sequence of bytes, or an object that generates them.
"""

import sys
from .msg import Message

py2 = (sys.version_info.major == 2)


class Parser(object):
    """MIDI Parser

    Parses a stream of bytes and produces messages.

    Data can be put into the parser in the form of
    integers, bytearrays or byte strings.
    """

    def __init__(self):
        """Create a new parser."""
        self.messages = []
        self.reset()
        self._msg = None  # Current message
        self._data = None  # Sysex data

    def reset(self):
        """Reset the parser.

        This will remove all parsed messages."""
        self._msg = None
        self._data = None

    def num_pending(self):
        """Return the number of messages ready to be received."""
        return len(self.messages)

    def put_byte(self, byte):
        """Put one byte into the parser.

        The byte must be an integer in range 0 - 255.

        (This function does all the work of parsing the
        byte stream.)
        """
        try:
            int(byte)
        except TypeError:
            fmt = 'argument must be an integer (was {!r})'
            raise TypeError(fmt.format(byte))

        if not 0 <= byte < 0x100:
            fmt = 'byte out of range: {!r}'
            raise ValueError(fmt.format(byte))

        # Todo: enforce type and range of 'byte'

        #
        # Handle byte
        #
        if byte >= 0x80:
            # New message
            status_byte = byte

            if 0xf8 <= status_byte <= 0xff:
                #
                # Realtime message. These have no databytes,
                # so they can be appended right away.
                #
                self.messages.append(Message(status_byte))
            elif status_byte == 0xf7:
                #
                # End of sysex
                #
                if self._msg:
                    self._msg.data = self._data
                    self.messages.append(self._msg)
                    self.reset()
                else:
                    pass  # Stray sysex_end byte. Ignore it.
            else:
                #
                # Start of message
                #
                self._msg = Message(status_byte)
                self._data = []

        else:
            #
            # Data byte (can possibly complete message)
            #

            if self._msg:
                self._data.append(byte)

                if len(self._data) == self._msg.spec.size - 1:
                    self._add_data(self._msg, self._data)
                    self.messages.append(self._msg)
                    self.reset()

        return len(self.messages)

    def _add_data(self, msg, data):
        """Add data bytes that we have collected to the message.

        For internal use.
        """

        # Shortcuts
        spec = msg.spec

        names = list(spec.args)

        if msg.status_byte < 0xf0:
            # Channel was already handled above
            names.remove('channel')

        if msg.type == 'sysex':
            msg.data = data

        elif msg.type == 'pitchwheel':
            value = data[0] | (data[1] << 7)
            value -= (2 ** 13)  # Make this a signed value
            msg.value = value

        elif msg.type == 'songpos':
            value = data[0] | data[1] << 7
            msg.pos = value
        else:
            #
            # Only normal data bytes.
            # Just map them to names.
            #
            for (name, value) in zip(names, data):
                setattr(msg, name, value)

    def get_msg(self):
        """Get the first parsed message.

        Returns None if there is no message yet.
        """
        if self.messages:
            return self.messages.pop(0)
        else:
            return None

    def feed(self, data):
        """Feed MIDI data to the parser.

        Accepts any object that produces a sequence of integers in
        range 0 - 255, such as:

            [0, 1, 2]
            (0, 1, 2)
            [for i in range(256)]
            (for i in range(256)]
            bytearray()
            b''  # Will be converted to integers in Python 2.
        """
        if py2 and isinstance(data, str):
            # Byte strings in Python 2 need extra attention
            for char in data:
                self.put_byte(ord(char))
        else:
            for byte in data:
                self.put_byte(byte)

        return len(self.messages)

    def __iter__(self):
        """
        Yield pending messages.
        """

        while self.messages:
            yield self.messages.pop(0)


def parseall(data):
    """
    Parse MIDI data and return a list of all messages found.

    Todo: should return a generator?
    """

    p = Parser()
    p.feed(data)
    return list(p)


def parse(data):
    """
    Parse MIDI data and return
    the first message found, or None
    if no messages were found.
    """

    p = Parser()
    p.feed(data)
    return p.get_msg()
