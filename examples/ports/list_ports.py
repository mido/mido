#!/usr/bin/env python3
"""
List available ports.

This is a simple version of mido-ports.
"""
import mido


def print_ports(heading, port_names):
    print(heading)
    for name in port_names:
        print(f"    '{name}'")
    print()


print()
print_ports('Input Ports:', mido.get_input_names())
print_ports('Output Ports:', mido.get_output_names())
