#!/usr/bin/env python
"""
Receive messages from multiple ports.
"""
import mido

# Open all available inputs.
ports = [mido.input(name) for name in mido.input_names()]
for port in ports:
    print('Using {}'.format(port))
print('Waiting for messages...')

try:
    for message, port in multi_receive(ports):
        print('Received {}'.format(message))
except KeyboardInterrupt:
    pass
