#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Simple server that just prints every message it receives.

    python3 simple_server.py localhost:8080
"""
import sys

from mido import sockets

if sys.argv[1:]:
    address = sys.argv[1]
else:
    address = 'localhost:9080'

print(f'Serving on {address}')

host, port = sockets.parse_address(address)

with sockets.PortServer(host, port) as server:
    while True:
        try:
            client = server.accept(block=False)
            if client:
                for message in client:
                    print(message)
        except KeyboardInterrupt:
            break
