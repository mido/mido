"""
An easy way to create a corresponding note_on message to a note_off
message.
"""

from __future__ import print_function

import time
import random
import mido

def off(msg):
    if msg.type != 'note_on':
        raise ValueError('Message type must be note_on')

    # Alternatively, this could create a note_on with velocity=0.
    return mido.new('note_off', channel=msg.channel, note=msg.note)

for i in range(10):
    note = mido.new('note_on', note=random.randrange(128), velocity=100)

    # Print a note_on and a corresponding note_off.
    print(note)    
    print(off(note))
    print()
