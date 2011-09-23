#!/usr/bin/env python

from __future__ import print_function

"""
List portmidi devices.
"""

import pprint
import protomidi.portmidi as pm

def print_devices(devices):
    for dev in devices:
        if dev.opened:
            opened = '(opened)'
        else:
            opened = ''
        print('    {} {}'.format(repr(dev.name), opened))
    print()

print('Inputs:')
print_devices(pm.get_devices(input=1))

print('Outputs:')
print_devices(pm.get_devices(output=1))
