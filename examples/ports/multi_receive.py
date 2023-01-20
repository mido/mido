#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Receive messages from multiple ports.
"""
import mido
from mido.ports import multi_receive

# Open all available inputs.
ports = [mido.open_input(name) for name in mido.get_input_names()]
for port in ports:
    print(f'Using {port}')
print('Waiting for messages...')

try:
    for message in multi_receive(ports):
        print(f'Received {message}')
except KeyboardInterrupt:
    pass
