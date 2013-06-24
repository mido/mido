"""
Sends random notes to the output port.
"""

import sys
import time
import random

import mido
import mido.portmidi as pm


if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

out = pm.Output(portname)

notes = [60, 62, 64, 67, 69, 72]

#
# Play random notes with random programs
#
try:
    while 1:
        # out.send(mido.new('program_change', program=random.randrange(128)))
        
        # note = random.randrange(128)

        note = random.choice(notes)
        
        out.send(mido.new('note_on', note=note, velocity=100))
        time.sleep(0.05)
        
        out.send(mido.new('note_off', note=note, velocity=100))
        time.sleep(0.1)
except KeyboardInterrupt:
    pass
finally:
    # Send 'All Notes Off'
    out.send(mido.new('control_change', control=123, value=0))
