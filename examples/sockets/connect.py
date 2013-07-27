#!/usr/bin/env python
"""
Forward all messages from one or more ports to server.

Example:

    python connect.py localhost:8080 'Keyboard MIDI 1'
"""
import sys
import mido
from mido.sockets import SocketPort

hostname, port = mido.sockets.parse_address(sys.argv[1])
ports = [mido.open_input(name) for name in sys.argv[2:]]

with SocketPort(hostname, port) as server:
    for message in mido.ports.multi_receive(ports):
        print(message)
        server.send(message)
