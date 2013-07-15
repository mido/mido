#!/usr/bin/env python
"""
Example of non-blocking reception from input port.
"""

from __future__ import print_function
import sys
import time
import mido

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with mido.open_input(portname) as port:
        print('Using {}'.format(port))
        while 1:
            # Iterate through all messages
            # that are available at this time.
            for _ in range(port.pending()):
                message = port.receive()
                print('Received {}'.format(message))

            print('Doing something else for a while...')
            time.sleep(0.5)
except KeyboardInterrupt:
    pass
