#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Example of non-blocking reception from input port.
"""
import sys
import time

import mido

if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    with mido.open_input(portname) as port:
        print(f'Using {port}')
        while True:
            for message in port.iter_pending():
                print(f'Received {message}')

            print('Doing something else for a while...')
            time.sleep(0.5)
except KeyboardInterrupt:
    pass
