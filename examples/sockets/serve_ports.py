#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Serve one or more output ports.

Every message received on any of the connected sockets will be sent to
every output port.

Example:

    python3 serve_ports.py :8080 'SH-201' 'SD-20 Part A'

This simply iterates through all incoming messages. More advanced and
flexible servers can be written by calling the ``accept()`` and
``accept(block=False) methods directly. See PortServer.__init__() for
an example.
"""
import sys

import mido
from mido import sockets
from mido.ports import MultiPort

# Todo: do this with a argument parser.
out = MultiPort([mido.open_output(name) for name in sys.argv[2:]])

(host, port) = sockets.parse_address(sys.argv[1])
with sockets.PortServer(host, port) as server:
    for message in server:
        print(f'Received {message}')
        out.send(message)
