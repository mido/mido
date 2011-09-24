import time
import random
import pprint
import protomidi.portmidi as io
from protomidi.msg import *

output = io.Output('SH-201 MIDI 1')
while 1:
    note = random.randrange(128)
    output.send(note_on(note=note, velocity=127))
    time.sleep(0.5)
    output.send(note_off(note=note, velocity=127))
