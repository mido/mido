#!/usr/bin/env python

"""
List portmidi devices.
"""

from __future__ import print_function

import protomidi.portmidi as pm

def print_devices(devices):
    """
    Print all devices in the list.
    """
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
