"""
Prints message as they arrive on the input port.

.recv() blocks until there is a message available. .poll() will return
how many messages you can safely read without blocking, so you can
implement nonblocking read with:

    while input.poll():
        print(input.recv())
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
