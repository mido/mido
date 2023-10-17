#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Forward all messages from one or more ports to server.

Example:

    python3 forward_ports.py localhost:8080 'Keyboard MIDI 1'
"""
import sys

import mido

host, port = mido.port.sockets.parse_address(sys.argv[1])
ports = [mido.open_input(name) for name in sys.argv[2:]]

with mido.port.sockets.connect(host, port) as server_port:
    print('Connected.')
    for message in mido.port.ports.multi_receive(ports):
        print(f'Sending {message}')
        server_port.send(message)
