#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Send random notes to the output port.
"""

import random
import sys
import time

import mido
from mido import Message

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

try:
    with mido.open_output(portname, autoreset=True) as port:
        print(f'Using {port}')
        while True:
            note = random.choice(notes)

            on = Message('note_on', note=note)
            print(f'Sending {on}')
            port.send(on)
            time.sleep(0.05)

            off = Message('note_off', note=note)
            print(f'Sending {off}')
            port.send(off)
            time.sleep(0.1)
except KeyboardInterrupt:
    pass

print()
