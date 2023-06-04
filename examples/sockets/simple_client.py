#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Simple client that sends program_change messages to server at timed
intervals.

Example:

    python3 simple_client.py localhost:8080
"""
import random
import sys
import time

import mido

if sys.argv[1:]:
    address = sys.argv[1]
else:
    address = 'localhost:9080'

host, port = mido.sockets.parse_address(address)

notes = [60, 67, 72, 79, 84, 79, 72, 67, 60]
on = mido.Message('note_on', velocity=100)
off = mido.Message('note_off', velocity=100)
base = random.randrange(12)

print(f'Connecting to {address}')

with mido.sockets.connect(host, port) as server_port:
    try:
        message = mido.Message('program_change')
        for note in notes:
            on.note = off.note = base + note

            server_port.send(on)
            time.sleep(0.05)

            server_port.send(off)
            time.sleep(0.1)
    finally:
        server_port.reset()
