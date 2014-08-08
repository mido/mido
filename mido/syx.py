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

    Messages other than sysex will be ignored.
    """
    with open(filename, 'rb') as infile:
        data = infile.read()

    if data[0] == b'\xf0':
        # Binary.
        return parse_all(data)
    else:
        parser = Parser()

        # Plain text.
        for lineno, line in enumerate(data.split('\n'), start=1):
            for byte in line.split():
                if len(byte) != 2:
                    raise IOError(
                        '{!r}, line {}: hex byte must be 2 characters'.format(
                            filename, lineno))

                try:
                    byte = int(byte, 16)
                except ValueError:
                    raise IOError('{!r}, line {}: '
                                  'Invalid hex byte {!r}'.format(
                                      filename, lineno, byte[:2]))
                parser.feed_byte(byte)

        return [message for message in parser if message.type == 'sysex']


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
