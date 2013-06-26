"""
MIDI Parser

The API of the Parser class will change to make it more consistent and
useful. This class should be considered internal to Mido for now.

Current API (more or less):

    Parser()
        feed(data)
        put_byte(byte)
        get_msg() -> Message or None
        reset()
        __iter__()    iterate through available messages

    parse(data) -> Message or None
    parseall(data) -> [Message, ...]

byte is an integer in range 0 - 255.
data is any sequence of bytes, or an object that generates them.

API notes

Required functionality:
    - put one byte into the parser
    - put a sequence of bytes into the parser
    - check how many messages are available
    - get one message

Possibly useful functionality:
    - get all messages as a list
    - iterate through available messages
    - reset parser (or you could just make a new parser)
"""

import sys
from collections import deque
from .msg import Message, MIN_PITCHWHEEL

py2 = (sys.version_info.major == 2)


class Parser(object):
    """
    MIDI Parser

    Parses a stream of bytes and produces messages.

    Data can be put into the parser in the form of
    integers, bytearrays or byte strings.
    """

    def __init__(self):
        """Create a new parser."""
        self._messages = deque()
        self._msg = None  # Current message
        self._data = []  # Sysex data

    def reset(self):
        """Reset the parser.

        This will remove all parsed messages."""
        self._messages.clear()
        self._msg = None
        self._data = []

    # Not sure what to name this.
    #
    # def available_messages(self):
    #     """Return the number of messages available for get_msg()."""
    #     return len(self._messages)

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

        if not 0 <= byte < 256:
            fmt = 'byte out of range: {!r}'
            raise ValueError(fmt.format(byte))

        #
        # Handle byte
        #
        if byte >= 0x80:
            # New message
            status_byte = byte

            if 0xf8 <= status_byte <= 0xff:
                # Realtime message. These have no databytes,
                # so they can be appended right away.
                self._messages.append(Message(status_byte))
            elif status_byte == 0xf7:
                # End of sysex
                if self._msg:
                    self._msg.data = self._data
                    self._messages.append(self._msg)
                    self._msg = None
                    self._data = []
                else:
                    pass  # Stray sysex_end byte. Ignore it.
            else:
                # Start of message
                self._msg = Message(status_byte)
        else:
            # Data byte (can possibly complete message)
            if self._msg:
                self._data.append(byte)

                if len(self._data) == self._msg.spec.size - 1:
                    self._add_data(self._msg, self._data)
                    self._messages.append(self._msg)
                    self._msg = None
                    self._data = []

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
            # Pitch is a 14 bit signed integer.
            v = data[0] | (data[1] << 7)
            # Make value value signed by
            # adding the minimum value.
            msg.pitch = v + MIN_PITCHWHEEL

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
        if self._messages:
            return self._messages.popleft()
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

    def __iter__(self):
        """Yield messages that have been parsed so far."""
        # 
        # This is a 'while count():' loop rather than 'for msg in
        # self._messages:' to allow the caller to break out of the
        # loop before consuming all of the messages. (This was used in
        # the PortMIDI input port.)
        # 
        while len(self._messages):
            yield self._messages.popleft()


def parseall(data):
    """Parse MIDI data and return a list of all messages found.

    This is typically used to parse a little bit of data with a few
    messages in it. It's best to use a Parser object for larger
    amounts of data. Also, tt's often easier to use parse() if you
    know there is only one message in the data.
    """
    p = Parser()
    p.feed(data)
    return list(p)


def parse(data):
    """ Parse MIDI data and return the first message found.

    Data after the first message is ignored. Use parseall()
    to parse more than one message.
    """
    p = Parser()
    p.feed(data)
    return p.get_msg()
