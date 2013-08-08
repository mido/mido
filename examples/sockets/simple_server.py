#!/usr/bin/env python
"""
Simple server that just prints every message it receives.

    python simple_server.py localhost:8080
"""
import sys
import time
import mido
from mido import sockets
from mido.ports import MultiPort

try:
    (hostname, port) = sockets.parse_address(sys.argv[1])
    with sockets.Server(hostname, port) as server:
        for message in server:
            print(message)
except KeyboardInterrupt:
    pass
