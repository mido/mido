from .msg import opcode2typeinfo, opcode2msg

"""
MIDI parser

Todo:
  - test parser with random data, text files etc.
    (it should never crash, just return whatever
     valid data it can find. Perhaps complain, but
     not stop the program.)
"""

class Parser:
    """
    Usage:

        p = Parser()
        p.feed(data)
        for msg in p:
            use(msg)

    To get all messages as a list:

        messages = list(p)

    Todo:
       - refine API
       - add method that returns the number of pending messages?
    """

    def __init__(self):
        self._messages = []
        self._reset()

    def _reset(self):
        """
        Reset parser for new message.
        """
        self._inmsg = False
        self._bytes = None       
        self._typeinfo = None

    def feed_byte(self, byte):
        # Todo: this is silly. Shouldn't it be the other way around?
        self.feed(chr(byte))
        
    def feed(self, mididata):
        """
        Feed MIDI data to the parser. 'mididata'
        is a bytearray or bytes of data to parse.

        Returns the number of pending messages.
        """

        if isinstance(mididata, bytearray):
            pass  # All OK
        elif isinstance(mididata, bytes):
            mididata = bytearray(mididata)
        else:
            raise ValueError('mididata must be bytearray or bytes')

        for byte in mididata:
            if byte >= 128:
                # New message
                opcode = byte

                if 0xf8 <= opcode <= 0xff:
                    # Realtime message. This can be
                    # interleaved in other messages.
                    # Just append it now.
                    self._messages.append(opcode2msg[opcode])

                elif opcode == 0xf7:
                    # End of sysex
                    # Crete message.

                    # Todo: handle case where end of sysex is reached too
                    # early.
                    manifacturer = self._bytes[1]
                    data = tuple(self._bytes[2:])
                    msg = opcode2msg[0xf0](manifacturer=manifacturer, data=data)

                    self._messages.append(msg)
                    self._reset()
                else:
                    # Normal message.
                    # Set up parser.
                    self._inmsg = True
                    self._typeinfo = opcode2typeinfo[opcode]
                    self._bytes = []
                    self._bytes.append(opcode)

            else:
                # Data byte

                if self._inmsg:
                    self._bytes.append(byte)
                else:
                    # Ignore stray data byte
                    pass


            #
            # End of message?
            #
            if self._inmsg:
                # Todo: what happens to sysex messges here?

                if len(self._bytes) == self._typeinfo.size:
                    opcode = self._bytes[0]
                    data = self._bytes[1:]
                    typeinfo = self._typeinfo  # Shortcut

                    # Get message prototype.
                    # This will get the right channel for us even.
                    msg = opcode2msg[opcode]

                    names = list(typeinfo.names)
                    if opcode <= 0xf0:
                        # Channel was already handled above
                        names.remove('channel')

                    # Time can't be parsed
                    names.remove('time')

                    if len(names) == len(data):

                        # No conversion necessary. Only normal data bytes
                        args = {}
                        for (name, value) in zip(names, data):
                            args[name] = value

                        msg = msg(**args)

                    elif msg.type == 'pitchwheel':
                        lsb = data[0]
                        msb = data[1]
                        value = data[0] | (data[1] << 7)
                        value -= (2**13)  # Make this a signed value
                        msg = msg(value=value)

                    elif msg.type == 'songpos':
                        value = data[0] | data[1] << 7
                        msg = msg(pos=value)
                    else:
                        # Unknown message. This should never happen.
                        # Todo: How do we handle this?
                        msg = None
                        
                    if msg:
                        self._messages.append(msg)
                    self._reset()

        return len(self._messages)

    def get_msg(self):
        """
        Get the first pending message.

        Returns None if there is no message yet.
        """
        if self._messages:
            return self._messages.pop(0)
        else:
            return None

    def __iter__(self):
        """
        Yield pending messages.
        """

        for msg in self._messages:
            yield msg

        self._messages = []

def parse(mididata):
    """
    Parse MIDI data and return any messages found.

    Todo: should return a generator?
    """

    p = Parser()
    p.feed(mididata)
    return list(p)
