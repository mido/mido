#!/usr/bin/env python

from __future__ import print_function

"""
List portmidi devices.

 {'id': 9,
  'input': 0,
  'interf': 'ALSA',
  'name': 'qjackctl',
  'opened': 0,
  'output': 1}]
"""

import pprint
import protomidi.portmidi as pm

def print_devices(devices):
    for dev in devices:
        if dev['opened']:
            opened = '(opened)'
        else:
            opened = ''
        print('    {} {}'.format(dev['name'], opened))
    print()

devices = pm.get_devinfo()

print('Inputs:')
print_devices([dev for dev in devices if dev['input']])

print('Outputs:')
print_devices([dev for dev in devices if dev['output']])
