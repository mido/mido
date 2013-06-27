#!/usr/bin/env python
"""
List available PortMidi ports.
"""

from __future__ import print_function
import sys
from mido.portmidi import get_input_names, get_output_names

python2 = (sys.version_info.major == 2)


def print_ports(heading, port_names):
    print(heading)
    for name in port_names:
        print("    '{}'".format(name))
    print()


print()
print_ports('Input Ports:', get_input_names())
print_ports('Output Ports:', get_output_names())
