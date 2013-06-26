"""
Print messages as they arrive on the input port.

.recv() blocks until there is a message available. .poll() will return
how many messages you can safely read without blocking, so you can
implement nonblocking read with:

    while 1:
        while input.poll():
            msg = input.recv()
            print(msg)

        # ... do something else
"""

from __future__ import print_function

import sys
import mido
import mido.portmidi as pm

if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

input = pm.Input(portname)
while 1:
    msg = input.recv()
    print(msg.hex(), ' ', msg)
