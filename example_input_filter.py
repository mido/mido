"""
Receive messages on the input port and print messages with a specific
channel (defaults to 0).

Usage:

    python example_input_filter.py portname [CHANNEL] [...]
"""

from __future__ import print_function
import sys
import mido
from mido.portmidi import Input

def accept_notes(port):
    """Only let note_on and note_off messages through."""
    for msg in port:
        if msg.type in ('note_on', 'note_off'):
            yield msg

if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None   # Use default port

try:
    with Input(portname) as port:
        print("Using input '{}'".format(port.name))
        for message in accept_notes(port):
            print('{}  {}'.format(message.hex(), message))
except KeyboardInterrupt:
    pass
