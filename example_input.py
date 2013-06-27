#!/usr/bin/env python
"""
Receive messages from the input port and print them out.
"""

from __future__ import print_function
import sys
import mido
from mido.portmidi import Input

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with Input(portname) as port:
        print("Using input '{}'".format(port.name))
        for message in port:
            print('{}  {}'.format(message.hex(), message))
except KeyboardInterrupt:
    pass
