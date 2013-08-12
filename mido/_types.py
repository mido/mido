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
