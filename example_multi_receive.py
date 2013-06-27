#!/usr/bin/env python
"""
Receive messages from multiple ports.
"""

from mido.portmidi import Input, get_input_names
from mido.ports import multi_receive

# Open all available inputs.
ports = [Input(name) for name in get_input_names()]
for port in ports:
    print("Using input '{}'".format(port.name))
print('Waiting for messages...')

try:
    for message, port in multi_receive(ports):
        print('Received {} from {}'.format(message.type, port.name))
except KeyboardInterrupt:
    pass
