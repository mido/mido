"""
Prints a hexadecimal representation of every message received on the
default input.
"""

import time
import mido
import mido.portmidi as pm

input = pm.Input()
while 1:
    #
    # Input.recv() doesn't currently block, so
    # we need to check if a message was received,
    # and if not, wait a bit and try again.
    #
    # This will most likely change.
    #
    msg = input.recv()
    if msg:
        print(msg.hex())
    else:
        time.sleep(0.001)

