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

def read_syx(filename):
    """Read sysex messages from SYX file.

    This handles both the text (hexadecimal) and binary formats.

    Messages other than sysex will be ignored.  In text files it will
    ignore any non-hexadecimal characters, and strip the last
    character if there are an odd number of hex digits in the file.
    """
    with open(filename, 'rb') as infile:
        data = infile.read()

    if not data:
        return
    
    if data[0] != b'\xf0':
        # Remove any characters that are not hex digits.
        text = b''.join([byte for byte in data if byte in _HEXDIGITS])

        # Remove the last digit in odd-length string to make
        # binascii happy.
        if len(text) % 2:
            text = text[:-1]
            
        data = binascii.a2b_hex(text)

    return parse_all(data)


def write_syx(filename, messages, plaintext=False):
    """Write sysex messages to a SYX file.

    Messages other than sysex will be skipped.

    By default this will write the binary format.  Pass
    ``plaintext=True`` to write the plain text format (hex encoded
    ASCII text).
    """
    messages = [m for m in messages if m.type == 'sysex']

    if plaintext:
        with open(filename, 'wb') as outfile:
            for message in messages:
                outfile.write(message.bin())
    else:
        with open(filename, 'wt') as outfile:
            for message in messages:
                outfile.write(message.hex())
                outfile.write('\n')
