"""
Send random notes to the output port.
"""

import sys
import time
import random

import mido
from mido.portmidi import Output


if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

# A pentatonic scale
notes = [60, 62, 64, 67, 69, 72]

try:
    with Output(portname) as port:
        while 1:
            note = random.choice(notes)
            
            port.send(mido.new('note_on', note=note, velocity=100))
            time.sleep(0.05)
            
            port.send(mido.new('note_off', note=note, velocity=100))
            time.sleep(0.1)
except KeyboardInterrupt:
    print()
finally:
    # Send 'All Notes Off'
    port.send(mido.new('control_change', control=123, value=0))
