import random
from protomidi.msg import *
import protomidi.portmidi as pm

import time

out = pm.Output()

#
# Play random notes with random programs
#
while 1:
    out.send(mido.new('program_change', program=random.randrange(128)))

    note = random.randrange(128)

    out.send(mido.new('note_on', note=note, velocity=100))
    time.sleep(0.1)

    out.send(mido.new('note_off', note=note, velocity=100))
    time.sleep(0.1)
