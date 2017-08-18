import sys

PY2 = (sys.version_info.major == 2)


def convert_py2_bytes(data):
    """Convert bytes object to bytearray in Python 2.

    Many parts of Mido such as ``Parser.feed()`` and
    ``Message.from_bytes()`` accept an iterable of integers.

    In Python 3 you can pass a byte string::

        >>> list(b'\x01\x02\x03')
        [1, 2, 3]

    while in Python 2 this happens::

        >>> list(b'\x01\x02\x03')
        ['\x01', '\x02', '\x03']

    This function patches over the difference::

        >>> list(convert_py2_bytes(b'\x01\x02\x03'))
        [1, 2, 3]

    """
    if PY2 and isinstance(data, bytes):
        return bytearray(data)
    else:
        return data
