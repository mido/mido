import collections
from .msg import messages, opcode2typeinfo


class Parser:
    """
    MIDI parser
    """
    
    def __init__(self):
        self.opcode = None
        self.info = None
        self.bytes = bytearray()

        self.pending = collections.deque()

    def poll(self):
        """
        Return the number of pending messages.
        """
        return len(self.pending)

    def feed(self, data):
        """
        Feed bytes to the parser. bytearray or bytes.
        """

        # Todo: typecheck

        # Convert to byte array if necessary
        bytes = bytearray(data)

        for byte in bytes:
            if byte >= 128:
                opcode = byte
                if 0xf8 <= opcode <= 0xff:
                    # Realtime messages have no data,
                    # so they can cut in line.
                    self.pending.append(opcode2msg[opcode])
                else:
                    # Set opcode, and reset data array
                    self.opcode = opcode
                    self.info = opcode2info[opcode]
                    self.bytes = bytearray()
            else:
                # data byte
                if self.opcode:
                    self.bytes.append(byte)
                else:
                    pass  # Ignore data bytes outside messages

        if self.opcode and len(self.bytes) == self.info.size:
            if self.info.type != 'sysex':
                pass  # Build message

    def __iter__(self):
        while self.pending:
            yield self.pending.popleft()
    
    def fetchone(self):
        if not poll():
            raise ValueError('There are no pending MIDI messages in the parser')
        return self.pending.popleft()

    def fetchall(self):
        return list(self)
    
