from .msg import opcode2typeinfo, opcode2msg 

def parse(midibytes):
    """
    Parse MIDI data and yield messages as they are completed.

    midibytes is a bytes or bytearray object of MIDI bytes to read.
    (Todo: support reading from file.)

    Usage:

        for msg in parse(midibytes):
             use(msg)

    This parser has the limitation that it will only yield when it
    has collected a full message. Thus it can not be used to parse
    a live MIDI stream, as that could end up blocking the application
    if the rest of a message never arrives.

    I will write another version of the parser to be used for
    live streams.
    """

    # Todo: handle sysex

    opcode = None    # Not currently inside a message
    bytes = None     # Used to data bytes
    typeinfo = None  # Message type info (name, size etc.)

    for byte in midibytes:
        if byte >= 128:            
            opcode = byte

            if 0xf8 <= opcode <= 0xff:
                # Realtime message. This can be
                # interleaved in other messages.
                # Just yield it now.
                yield opcode2msg[opcode]
                
            elif opcode == 0xf7:
                # End of sysex
                # Crete message and yield it
                
                # Todo: handle case where end of sysex is reached too
                # early.
                vendor = bytes[0]
                data = tuple([ord(b) for b in bytes])
                msg = opcode2msg[opcode](vendor=vendor, data=data)

                yield msg

                opcode = None
            else:
                typeinfo = opcode2typeinfo[opcode]
                bytes = bytearray()  # Collect data bytes here

        elif opcode:
            bytes.append(byte)
        
        else:
            # Byte found outside message, ignoring it 
            # (Todo: warn user?)
            pass

        if opcode and len(bytes) == typeinfo.size:
            if typeinfo.type == 'sysex':
                # Sysex is longer than its 'size' field
                # would sugges, since it also has a variable
                # number of data bytes.
                pass
            else:
                pass  # Todo: build Message

class Parser:
    """
    Usage:

        p = Parser()
        if p.feed(data)
            for msg in p:
                use(msg)
    """

    def __init__(self, stream):
        self.stream = stream
    
    def feed(self, mididata):
        """
        Feed MIDI data to the parser.

        Returns the number of pending messages.
        """

        pass


    def __iter__(self):
        """
        Yield pending messages.
        """
