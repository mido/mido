#!/usr/bin/env python
"""
List available PortMidi ports.
"""

from __future__ import print_function
import sys
import mido

def print_ports(heading, port_names):
    print(heading)
    for name in port_names:
        print("    '{}'".format(name))
    print()

print()
print_ports('Input Ports:', mido.get_input_names())
print_ports('Output Ports:', mido.get_output_names())
