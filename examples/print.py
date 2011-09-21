#!/usr/bin/env python

"""
Print out anything coming in on the input port.
"""

from __future__ import print_function
import sys
import time
import pprint
import protomidi.portmidi

if sys.argv[1:]:
    dev = int(sys.argv[1])
else:
    for devinfo in protomidi.portmidi.get_devinfo():
        if devinfo['input']:
            print(devinfo['id'], devinfo['name'])

    sys.exit(0)

input = protomidi.portmidi.Input(dev)
while 1:
    msg = input.recv()
    if msg:
        print(msg)
    time.sleep(0.001)
