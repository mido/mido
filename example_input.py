"""
Print messages as they arrive on the input port.
"""

from __future__ import print_function
import sys
import mido
from mido.portmidi import Input

if sys.argv[1:]:
    portname = sys.argv[1]
else:
    portname = None  # Use default port

try:
    for message in Input(portname):
        print('{}  {}'.format(message.hex(), message))
except KeyboardInterrupt:
    pass
