import struct

def signed(to_type, n):
    formats = {
        'byte': 'Bb',
        'short': 'Hh',
        'long': 'Ll',
        'ubyte': 'bB',
        'ushort': 'hH',
        'ulong': 'lL',
        }

    try:
        pack_format, unpack_format = formats[to_type]
    except KeyError:
        raise ValueError('invalid integer type {}'.format(to_type))

    try:
        packed = struct.pack(pack_format, n)
        return struct.unpack(unpack_format, packed)[0]
    except struct.error as err:
        raise ValueError(*err.args)

def unsigned(to_type, n):
    return signed('u{}'.format(to_type), n)

def encode_variable_int(value):
    """Encode variable length integer.

    Returns the integer as a list of bytes,
    where the last byte is < 128.

    This is used for delta times and meta message payload
    length.
    """
    if not isinstance(value, int) or value < 0:
        raise ValueError('variable int must be a positive integer')

    bytes = []
    while value:
        bytes.append(value & 0x7f)
        value >>= 7

    if bytes:
        bytes.reverse()

        # Set high bit in every byte but the last.
        for i in range(len(bytes) - 1):
            bytes[i] |= 0x80
        return bytes
    else:
        return [0]
