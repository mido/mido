#!/usr/bin/env python

import sys
import time
from protomidi import portmidi

portmidi.debug = True

input = portmidi.Input(sys.argv[1])

while 1:
    for msg in input:
        pass  # Just clear out the message list
    time.sleep(0.01)
