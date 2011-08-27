"""
Todo:

   - in msg.py: move msg_spec to top of file in msg.py
   
   - callback option?

       def callback(msg):

   - handle sysex
"""


import collections

import msg


def _opcode_is_system_realtime(opcode):
    """
    
    """
    return f8 <= opcode <= ff

Message = collections.namedtuple('Message', 'opcode data')


class Parser:
    """
    MIDI parser
    """
    
    def __init__(self, callback=False):
        self._opcode = None
        self._data = []
        self._pending = collections.deque()
        self.callback = callback

    def poll(self):
        """
        Return the number of pending messages.
        """
        return len(self._pending)

    def _send(self, msg):
        """
        Send msg back to the caller.

        Todo: rename function (_produce()?)
        """
        if self.callback:
            callback(msg)
        else:
            self._pending.append(msg)

    def put(self, byte):
        """
        Put on byte (an integer) into the parser.
        """
        if not isinstance(byte, int):
            raise TypeError('byte must be an int')

        b = bytearray()
        b.append(byte)
        self.feed(b)

    def feed(self, data):
        """
        Feed bytes to the parser. bytearray or bytes.
        """

        if isinstance(data, bytearray):
            pass
        elif isinstance(data, bytes):
            data = bytearray(bytes)
        else:
            raise TypeError('data must be of type bytes or bytearray')

        # Convert to byte array if necessary
        bytes = bytearray(bytes)

        for byte in data:
            if byte >= 128:
                opcode = byte

                # New opcode
                if _opcode_is_system_realtime(opcode):
                    # Realtime messages have no data,
                    # so they can cut in line.
                    self._send(byte)
                else:
                    # Set opcode, and reset data list
                    self._opcode = byte
                    self._data = []
            else:
                # data byte
                if self._opcode:
                    self._data.append(byte)
                else:
                    pass  # Ignore data bytes outside messages
            
            if len(self._bytes) == len(opcode2msg[opcode]):
                self._send_(self._opcode, self._data)
                self._opcode = None
                self._data = []

    def __iter__(self):
        while self._pending:
            yield self._pending.popleft()
    
    def fetchone(self):
        if not poll():
            raise ValueError('There are no pending MIDI messages in the parser')
        return self._pending.popleft()

    def fetchall(self):
        return list(self)
    
