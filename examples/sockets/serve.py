#!/usr/bin/env python
"""
Server one or more output ports.

Every message received on any of the connected sockets will be sent to
all ports.

For example:

    python serve.py :8080 'SH-201' 'SD-20 Part A'
"""
import sys
import time
import mido
from mido import sockets
from mido.ports import multi_iter_pending

# Todo: do this with a argument parser.
out = mido.ports.Broadcast([mido.open_output(name) for name in sys.argv[2:]])

(hostname, port) = sockets.parse_address(sys.argv[1])
with sockets.PortServer(hostname, port, backlog=10) as server:
    for message in server:
        print('Received {}'.format(message))
        out.send(message)
