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

    Or:
        p.feed(data)
        messages = p.getall()

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
        self._opcode = None     # Opcode
        self._data = None       # Data bytes
        self._typeinfo = None

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
                    manifacturer = self._data[0]
                    data = tuple(self._data[1:])
                    msg = opcode2msg[opcode](manifacturer=manifacturer, data=data)

                    self._messages.append(msg)
                    self._reset()
                else:
                    # Normal message.
                    # Set up parser.
                    self._opcode = opcode
                    self._typeinfo = opcode2typeinfo[opcode]
                    self._data = bytearray()  # Collect data bytes here

            elif self._opcode:
                # Already inside a message, append data byte
                self._data.append(byte)

            else:
                # Byte found outside message, ignoring it 
                # (Todo: warn user?)
                pass


            #
            # End of message?
            #
            msgsize = (1 + len(self._data))
            if msgsize == self._typeinfo.size:
                data = self._data  # Just a shortcut

                # Get message prototype.
                # This will get the right channel for us even.
                msg = opcode2msg[self._opcode]

                names = list(self._typeinfo.names)
                if opcode <= 0xf0:
                    # This was already done for us above.
                    names.remove('channel')

                if len(names) == len(data):

                    # No conversion necessary. Only normal data bytes
                    args = {}
                    for (name, value) in zip(names, data):
                        args[name] = value

                    msg = msg(**args)

                elif msg.type == 'pitchwheel':
                    # Todo: check if value is computed correctly
                    value = (float(data[0] | data[1] << 7) * 2) / 16384
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

    def getall(self):
        """
        Return all pending messages.
        """

        ret = self._messages
        self._messages = []

        return ret
    
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

    Todo: should be iterator?
    """

    p = Parser()
    p.feed(mididata)
    return p.getall()
