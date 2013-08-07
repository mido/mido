#!/usr/bin/env python
"""
Simple server that just prints every message it receives.

Only one client can connect at a time.

    python simple_server.py localhost:8080
"""
import sys
import time
import mido
from mido import sockets
from mido.ports import MultiPort

# Todo: do this with a argument parser.
out = MultiPort([mido.open_output(name) for name in sys.argv[2:]])

try:
    (hostname, port) = sockets.parse_address(sys.argv[1])
    with sockets.Server(hostname, port) as server:
        while 1:
            client = server.accept()
            print('Connection from {}'.format(client.name))
            for message in client:
                print(message)
            print('Client disconnected')
except KeyboardInterrupt:
    pass
