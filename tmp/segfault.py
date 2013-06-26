#!/usr/bin/env python

"""
This segfaults. Start Midi Keys, then run this script with 'python -i', wait for 2 seconds and
play something on Midi Keys. Boom, segfault.

NOTE: not tested with recent versions.
"""

from __future__ import print_function

import time
import random
import pprint
import traceback
import protomidi
from protomidi.msg import *
import protomidi.portmidi as pm

pm._flags['debug'] = True

try:
    out = pm.Output()
except IO:
    traceback.print_exc()

print('Sleeping for 2 seconds before opening input')
time.sleep(2)
print('Opening input')
input = pm.Input()
print('Please play something on Midi Keys now')

"""
while 1:
    note = random.randrange(128)

    out.send(note_on(note=note, velocity=75))
    time.sleep(0.25)
    out.send(note_off(note=note))
"""
