"""
Print messages as they arrive on the input port.

Input.receive() blocks until there is a message available. Input.poll()
will return how many messages you can safely read without blocking, so
you can implement nonblocking read with:

    while 1:
        for _ in range(port.poll()):
            message = port.receive()
            print(message)

        # ... do something else for a while
"""

from __future__ import print_function
import sys
import mido
from mido.portmidi import Input

if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    for message in Input(portname):
        print('{}  {}'.format(message.hex(), message))
except KeyboardInterrupt:
    pass
