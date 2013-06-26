"""
List available PortMidi ports.
"""

from __future__ import print_function

from mido.portmidi import get_input_names, get_output_names

def print_ports(heading, port_names):
    print(heading)
    for name in port_names:
        print('    {!r}'.format(name))
    print()

print()
print_ports('Input Ports:', get_input_names())
print_ports('Output Ports:', get_output_names())
