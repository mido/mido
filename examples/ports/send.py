#!/usr/bin/env python
"""
Send random notes to the output port.
"""

from __future__ import print_function
import sys
import time
import random
import mido


if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

def send(message, sleep_time):
    print('Sending {}'.format(message))
    port.send(message)
    time.sleep(sleep_time)

on = mido.Message('note_on')
off = mido.Message('note_off')

with mido.open_output(portname, autoreset=True) as port:
    print('Using {}'.format(port))
    while 1:
        on.note = off.note = random.choice(notes)
        send(on, 0.05)
        send(off, 0.1)
print()
