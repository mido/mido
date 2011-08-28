from .msg import opcode2info, opcode2msg 

def parse(mididata):
    """
    Parse MIDI data and yield messages as they are completed.

    mididata is a bytes or bytearray object of MIDI bytes to read.
    """

    # Todo: handle sysex

    opcode = None  # Not currently inside a message
    bytes = None   # Used to data bytes
    info = None    # Message type info (name, size etc.)

    for byte in mididata:
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
                info = opcode2info[opcode]
                bytes = bytearray()  # Collect data bytes here

        elif opcode:
            self.bytes.append(byte)
        
        else:
            # Byte found outside message, ignoring it 
            # (Todo: warn user?)
            pass

        if self.opcode and len(self.bytes) == self.info.size:
            if self.info.type == 'sysex':
                # Sysex is longer than its 'size' field
                # would sugges, since it also has a variable
                # number of data bytes.
                pass
            else:
                pass  # Todo: build Message
