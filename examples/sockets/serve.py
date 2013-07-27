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
with sockets.PortServer(hostname, port) as server:
    clients = []

    while 1:
        # Update connection list.
        client = server.accept(block=False)
        if client:
            clients.append(client)
            print('New connection from {}:{}.'.format(
                    client.hostname, client.port))
        clients = [client for client in clients if not client.closed]

        # Receive and send messages.
        for message in multi_iter_pending(clients):
            print(message)
            out.send(message)

        time.sleep(0.001)
