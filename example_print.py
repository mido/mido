#!/usr/bin/env python

"""
Print out anything coming in on the input port.
"""

from __future__ import print_function
import sys
import time
import pprint
import mido.portmidi as pm

if sys.argv[1:]:
    devname = sys.argv[1]
else:
    devname = None

input = pm.Input(devname)

while 1:
    msg = input.recv()
    if msg:
        print(msg)
    time.sleep(0.001)
