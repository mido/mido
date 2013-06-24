"""
MIDI parser

    Basic usage:

        p = Parser()

        # Note on
        p.put_byte(0x90)
        p.put_byte(60)
        p.put_byte(127)

        msg = p.get_msg()  # Returns the next message or None

    Convenience methods:

        p = Parser()
        p.feed(b'\x90\x23\x7f')      # note_on
        p.feed([0x80, 0x23, 0x7f])  # note_off

        print(parse([0x80, 0x23, 0x7f]))

    or just:

        for msg in parseall('\x90\x23\x7f\x90\x23\x00'):
            print(msg)

    p.messages   # A list of messages that have been parsed
    p.reset()    # Reset the parser

Todo:
   - refine API
   - add method that returns the number of pending messages?
"""

from .msg import Message, opcode2spec

class Parser:
    """
    MIDI Parser.
    """

    def __init__(self):
        self.messages = []
        self.reset()

    def reset(self):
        """
        Reset the parser.
        """
        self._msg = None  # Current message
        self._data = None  # Sysex data

    def num_pending(self):
        """
        Return the number of messages ready to be received.
        """
        return len(self.messages)

    def put_byte(self, byte):
        """
        Put one byte into the parser. 'byte' must be an integer
        in range(0, 256).
        """

        # Todo: enforce type and range of 'byte'

        #
        # Handle byte
        #
        if byte >= 0x80:
            # New message
            opcode = byte

            if 0xf8 <= opcode <= 0xff:
                #
                # Realtime message. These have no databytes,
                # so they can be appended right away.
                #
                self.messages.append(Message(opcode))
            elif opcode == 0xf7:
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
                self._msg = Message(opcode)  # This will split opcode and channel
                self._data = []

        else:
            #
            # Data byte (can possibly complete message)
            #

            if self._msg:
                self._data.append(byte)

                if len(self._data) == self._msg.spec.size-1:
                    self._add_data(self._msg, self._data)
                    self.messages.append(self._msg)
                    self.reset()

        return len(self.messages)

    def _add_data(self, msg, data):
        """
        Add data bytes that we have collected to the message.
        """

        # Shortcuts
        spec = msg.spec

        names = list(spec.args)

        if msg.opcode < 0xf0:
            # Channel was already handled above
            names.remove('channel')

        if msg.type == 'sysex':
            msg.data = data

        elif msg.type == 'pitchwheel':
            value = data[0] | (data[1] << 7)
            value -= (2**13)  # Make this a signed value
            msg.value = value

        elif msg.type == 'songpos':
            value = data[0] | data[1] << 7
            msg.pos = value
        else:
            #
            # Only normal data bytes.
            # Just map them to names.
            #
            args = {}
            for (name, value) in zip(names, data):
                setattr(msg, name, value)

    def get_msg(self):
        """
        Get the first pending message.

        Returns None if there is no message yet.
        """
        if self.messages:
            return self.messages.pop(0)
        else:
            return None

    def feed(self, data):
        """
        Feed MIDI data to the parser.

        'data' is a sequence of integers or a byte string
        of data to parse.

        Returns the number of pending messages.
        """
        if isinstance(data, bytes) and bytes is str:
            print('!')
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
