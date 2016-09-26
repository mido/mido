#!/usr/bin/env python
"""
Receive messages from the input port and print them out.
"""
from __future__ import print_function
import sys
import mido

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with mido.open_input(portname) as port:
        print('Using {}'.format(port))
        print('Waiting for messages...')
        for message in port:
            print('Received {}'.format(message))
            sys.stdout.flush()
except KeyboardInterrupt:
    pass
