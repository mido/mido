from .msg import opcode2typeinfo

def serialize(msg):
    """
    Return a bytearray representation of the message.
    """

    typeinfo = opcode2typeinfo[msg.opcode]

    data = bytearray()

    if hasattr(msg, 'channel'):
        data.append(msg.opcode | msg.channel)
    else:
        data.append(msg.opcode)

    for name in typeinfo.names:
        if name == 'channel':
            pass  # We already did this, skip it now
        
        elif name == 'data':
            for byte in msg.data:
                data.append(byte)  # Todo: extend()?
            
        elif msg.type == 'pitchwheel' and name == 'value':
            value = msg.value + (2**13)
            lsb = value & 0x7f
            msb = value >> 7
            data.append(lsb)
            data.append(msb)

        elif msg.type == 'songpos' and name == 'pos':
            # Convert 14 bit value to two 7-bit values
            # Todo: check if this is correct
            lsb = msg.pos & 0x7f
            data.append(lsb)

            msb = msg.pos >> 7
            print(msb)
            data.append(msb)
        else:
            # Ordinary data byte
            data.append(getattr(msg, name))

    if msg.type == 'sysex':
        data.append(0xf7)  # sysex_end

    return data
