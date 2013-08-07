#!/usr/bin/env python
"""
Forward all messages from one or more ports to server.

Example:

    python forward_ports.py localhost:8080 'Keyboard MIDI 1'
"""
import sys
import mido

host, port = mido.sockets.parse_address(sys.argv[1])
ports = [mido.open_input(name) for name in sys.argv[2:]]

with mido.sockets.connect(host, port) as server_port:
    print('Connected.')
    for message in mido.ports.multi_receive(ports):
        print('Sending {}'.format(message))
        server_port.send(message)
