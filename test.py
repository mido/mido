import random
import protomidi
from protomidi import portmidi
from protomidi.msg import *

import time


with portmidi.context():
    devices = portmidi.get_devinfo_dicts()

    # print(portmidi.get_defoutput())

    out = portmidi.Output(2)

    while 1:
        out.send(program(number=random.randrange(128)))
        note = random.randrange(128)
        out.send(note_on(note=note, velocity=100))
        time.sleep(0.1)
        out.send(note_off(note=note, velocity=100))
        time.sleep(0.1)
