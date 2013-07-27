#!/usr/bin/env python
"""
Simple client that sends program_change messages to server at timed
intervals.

Example:

    python simple_client.py localhost:8080
"""
import sys
import time
import random
import mido
from mido.sockets import SocketPort

hostname, port = mido.sockets.parse_address(sys.argv[1])
ports = [mido.open_input(name) for name in sys.argv[2:]]

with SocketPort(hostname, port) as server:
    message = mido.Message('program_change')
    for __ in range(10):
        message.program = random.randrange(128)
        server.send(message)
        time.sleep(0.2)
