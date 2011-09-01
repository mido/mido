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
                bytes.append(opcode)

        elif opcode:
            bytes.append(byte)
        
        else:
            # Byte found outside message, ignoring it 
            # (Todo: warn user?)
            pass


        #
        # End of message?
        #
        if len(bytes) == typeinfo.size:
            data = [b for b in bytes[1:]]
            # This will get the right channel for us even
            msg = opcode2msg[opcode]

            print('!!!', msg.type)

            names = list(typeinfo.names)
            if opcode <= 0xf0:
                names.remove('channel')

            if len(names) == len(data):

                # No conversion necessary. Only mornal data bytes
                args = {}
                for (name, value) in zip(names, data):
                    args[name] = value

                yield msg(**args)
            elif msg.type == 'pitchwheel':
                # Todo: check
                value = (float(data[0] | data[1] << 7) * 2) / 16384
                yield msg(value=value)
                
            elif msg.type == 'songpos':
                value = data[0] | data[1] << 7
                yield msg(pos=post)
            else:
                raise ValueError('Unsupported opcode %s' % opcode)

            opcode = None
            bytes = None
            typeinfo = None

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
