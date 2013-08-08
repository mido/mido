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

if sys.argv[1:]:
    address = sys.argv[1]
else:
    address = 'localhost:9080'

host, port = mido.sockets.parse_address(address)

notes = [60, 67, 72, 79, 84, 79, 72, 67, 60]
on = mido.Message('note_on', velocity=100)
off = mido.Message('note_off', velocity=100)
base = random.randrange(12)

print('Connecting to {}'.format(address))

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
