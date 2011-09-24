#!/usr/bin/env python

from __future__ import print_function

import time
import pprint
import protomidi
from protomidi.msg import *
import protomidi.portmidi as io

io.debug = True

input = io.Input()
while 1:
    for msg in input:
        print('   got:', msg)
    time.sleep(0.01)
