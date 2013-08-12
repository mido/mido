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
from .messages import Message, MIN_PITCHWHEEL, get_spec

PY2 = (sys.version_info.major == 2)


class Parser(object):
    """
    MIDI Parser

    Parses a stream of bytes and produces messages.

    Data can be put into the parser in the form of
    integers, byte arrays or byte strings.
    """

    def __init__(self):
        """Create a new parser."""
        self._parsed_messages = deque()
        self._reset()

    def _reset(self):
        self._spec = None
        self._bytes = []

    def _build_message(self):
        type_ = self._spec.type

        if type_ == 'sysex':
            arguments = {'data': self._bytes[1:]}

        elif type_ == 'pitchwheel':
            pitch = self._bytes[1]
            pitch |= ((self._bytes[2] << 7) + MIN_PITCHWHEEL)
            arguments = {'pitch': pitch}

        elif type_ == 'songpos':
            pos = self._bytes[1]
            pos |= (self._bytes[2] << 7)
            arguments = {'pos': pos}

        else:
            if self._bytes[0] < 0xf0:
                # Channel message. Skip channel.
                attribute_names = self._spec.arguments[1:]
            else:
                attribute_names = self._spec.arguments

            arguments = dict(zip(attribute_names, self._bytes[1:]))

        # Note: we're using the status byte here, not type.
        # If we used type, the channel would be discarded.
        return Message(self._bytes[0], **arguments)

    def _deliver(self, message):
        self._parsed_messages.append(message)

    def _handle_status_byte(self, byte):
        if 0xf8 <= byte <= 0xff:
            if self._spec:
                if self._bytes[0] == 0xf0:
                    try:
                        spec = get_spec(byte)
                    except LookupError:
                        return
                    self._deliver(Message(byte))
                else:
                    # Realtime message arrived inside a non-sysex
                    # message. Discard the message we were parsing.
                    self._reset()
            else:
                try:
                    self._spec = get_spec(byte)
                except LookupError:
                    return  # Skip unknown status byte.

                self._bytes = [byte]

        elif byte == 0xf7:
            # End of sysex
            if self._spec and self._bytes[0] == 0xf0:
                # We were inside a sysex message. Deliver it.
                self._deliver(self._build_message())
            self._reset()
        else:
            # Start of new message
            try:
                self._spec = get_spec(byte)
            except LookupError:
                return  # Skip unknown status byte.
            self._bytes = [byte]

    def _handle_data_byte(self, byte):
        self._bytes.append(byte)

        if self._spec:
            pass
        else:
            # Todo: handle delta time.
            pass

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
            self._handle_data_byte(byte)

        # If we have a complete messages, deliver it.
        if self._spec and len(self._bytes) == self._spec.length:
            self._deliver(self._build_message())

            if self._bytes[0] < 0xf0:
                # Delete data bytes, but keep the
                # status byte around to handle running
                # status.

                self._reset()
                #del self._bytes[1:]
            else:
                # System common messages have no running status.
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
