#!/usr/bin/env python
"""
Simple server that just prints every message it receives.

    python simple_server.py localhost:8080
"""
import sys
from mido import sockets

if sys.argv[1:]:
    address = sys.argv[1]
else:
    address = 'localhost:9080'

try:
    (hostname, portno) = sockets.parse_address(address)
    print('Serving on {}'.format(address))
    with sockets.PortServer(hostname, portno) as server:
        for message in server:
            print(message)
except KeyboardInterrupt:
    pass
