import random
import protomidi
from protomidi.msg import *
from protomidi.io import Input, Output, context, get_devinfo_dicts

import time

with context():

    devices = get_devinfo_dicts()
    # print(devices)

    out = Output(2)

    while 1:
        # Send random programchange
        out.send(program(number=random.randrange(128)))

        note = random.randrange(128)
        out.send(note_on(note=note, velocity=100))

        time.sleep(0.1)
        out.send(note_off(note=note, velocity=100))
        time.sleep(0.1)
