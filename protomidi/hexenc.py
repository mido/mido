#!/usr/bin/env python
"""
# This is a comment
9f 8f d9 _H _e _l _l _o __ _w _o _r _l _d d9 c9

' ' => '_'
'0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ' => 'A'
all others:     d9
Each byte is converted to three bytes.
"""

from __future__ import print_function, unicode_literals
import sys
import string

alphanum = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
legalchars = alphanum + '_'
hexchars = '0123456789abcdefABCDEF'
displaychars = string.digits + string.uppercase + string.lowercase + ' '

def encode(data, align=True):
    """
    Encode data as 
    """
    data = bytearray(data)
    ret = ''

    width = 0
    
    for byte in data:
        c = chr(byte)        
        if c in displaychars:
            if c == ' ':
                c = '_'  # Escape space as underscore

            if align:
                ret += '_'  # A leading underscore for alignment
            
            ret += c       # Print the character directly
        else:
            # Hex encode
            ret += ('%02x' % byte)

        if width > 70:
            ret += '\n'
            width = 0
        else:
            ret += ' '

            width += 3

    return ret

def decode(text):
    bytes = bytearray()

    while text:
        chrs = text[:3]
        text = text[3:]

        if chrs[0] == '.':
            bytes.append(orc(chrs[1]))
        else:
            bytes.append(int(chrs[:2], 16))

if __name__ == '__main__':
    if '--align' in sys.argv:
        align = True
    else:
        align = False

    data = sys.stdin.read()
    print(encode(data, align=align))
