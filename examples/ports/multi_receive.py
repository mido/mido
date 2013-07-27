#!/usr/bin/env python
"""
Receive messages from multiple ports.
"""
import mido
from mido.ports import multi_receive

# Open all available inputs.
ports = [mido.open_input(name) for name in mido.get_input_names()]
for port in ports:
    print('Using {}'.format(port))
print('Waiting for messages...')

try:
    for message in multi_receive(ports):
        print('Received {}'.format(message))
except KeyboardInterrupt:
    pass
