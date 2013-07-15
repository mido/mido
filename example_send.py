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

try:
    with mido.open_output(portname) as port:
        print('Using {}'.format(port))
        while 1:
            note = random.choice(notes)

            message = mido.Message('note_on', note=note, velocity=100)
            print('Sending {}'.format(message))
            port.send(message)
            time.sleep(0.05)
            
            message = mido.Message('note_off', note=note, velocity=100)
            print('Sending {}'.format(message))
            port.send(message)
            time.sleep(0.1)
except KeyboardInterrupt:
    print()
finally:
    # Send 'All Notes Off'
    port.send(mido.Message('control_change', control=123, value=0))
