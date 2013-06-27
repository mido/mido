#!/usr/bin/env python
"""
Send random notes to the output port.
"""

from __future__ import print_function
import sys
import time
import random

import mido
from mido.portmidi import Output


if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

def print_message(message):
    print('Sending {}  {}'.format(message.hex(), message))

try:
    with Output(portname) as port:
        print('Using {}'.format(port))
        while 1:
            note = random.choice(notes)

            message = mido.new('note_on', note=note, velocity=100)
            print_message(message)
            port.send(message)
            time.sleep(0.05)
            
            port.send(mido.new('note_off', note=note, velocity=100))
            print_message(message)
            port.send(message)
            time.sleep(0.1)
except KeyboardInterrupt:
    print()
finally:
    # Send 'All Notes Off'
    port.send(mido.new('control_change', control=123, value=0))
