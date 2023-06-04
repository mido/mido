#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Receive messages from the input port and print them out.
"""
import sys

import mido

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with mido.open_input(portname) as port:
        print(f'Using {port}')
        print('Waiting for messages...')
        for message in port:
            print(f'Received {message}')
            sys.stdout.flush()
except KeyboardInterrupt:
    pass
