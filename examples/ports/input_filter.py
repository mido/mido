#!/usr/bin/env python
"""
Receive messages on the input port and print messages with a specific
channel (defaults to 0).

Usage:

    python example_input_filter.py portname [CHANNEL] [...]
"""
from __future__ import print_function
import sys
import mido


def accept_notes(port):
    """Only let note_on and note_off messages through."""
    for message in port:
        if message.type in ('note_on', 'note_off'):
            yield message


if len(sys.argv) > 1:
    portname = sys.argv[1]
else:
    portname = None   # Use default port

try:
    with mido.open_input(portname) as port:
        print('Using {}'.format(port))

        print("Ignoring everything but 'note_on' and 'note_off'.")
        print('Waiting for notes...')

        for message in accept_notes(port):
            print('Received {}'.format(message))
except KeyboardInterrupt:
    pass
