"""
Read and write SYX file format
"""
from __future__ import print_function
import re
import string
import binascii
from .messages import Message
from .parser import Parser, parse_all

_HEXDIGITS = set(string.hexdigits.encode('ascii'))

def read_syx_file(filename):
    """Read sysex messages from SYX file.

    Returns a list of sysex messages.
    
    This handles both the text (hexadecimal) and binary
    formats. Messages other than sysex will be ignored. Raises
    ValueError if file is plain text and byte is not a 2-digit hex
    number.
    """
    def raise_value_error():
        raise ValueError('{!r} line {}: invalid hex byte {!r}'.format(
            filename, lineno, byte))

    with open(filename, 'rb') as infile:
        data = infile.read()

    if len(data) == 0:
        # Empty file.
        return []

    # data[0] will give a byte string in Python 2 and an integer in
    # Python 3.
    if data[0] in (b'\xf0', 240):
        # Binary.
        return parse_all(data)
    else:
        # Hex.
        # We're decoding as latin1 to avoid decoding errors.
        data = bytearray.fromhex(data.decode('latin1'))

        return [msg for msg in Parser(data) if msg.type == 'sysex']


def write_syx_file(filename, messages, plaintext=False):
    """Write sysex messages to a SYX file.

    Messages other than sysex will be skipped.

    By default this will write the binary format.  Pass
    ``plaintext=True`` to write the plain text format (hex encoded
    ASCII text).
    """
    messages = [m for m in messages if m.type == 'sysex']

    if plaintext:
        with open(filename, 'wt') as outfile:
            for message in messages:
                outfile.write(message.hex())
                outfile.write('\n')
    else:
        with open(filename, 'wb') as outfile:
            for message in messages:
                outfile.write(message.bin())
