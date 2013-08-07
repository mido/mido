#!/usr/bin/env python
"""
Receive messages from multiple ports.
"""
import mido
from mido.ports import MultiPort

# Open all available inputs.
ports = [mido.open_input(name) for name in mido.get_input_names()]
for port in ports:
    print('Using {}'.format(port))
print('Waiting for messages...')

multi = MultiPort(ports)
try:
    for message in multi:
        print('Received {}'.format(message))
except KeyboardInterrupt:
    pass
