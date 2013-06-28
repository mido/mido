#!/usr/bin/env python
"""
Unfinished example of IOPort usage.

This can be used to communicate with a device by sending and receiving
messages on the same port. In this case, you'd pass the same port name
to Input() and Output(). However, the two ports to do not have to pass
the same name to both.
"""

import mido
from mido.portmidi import Input, Output
from mido.ports import IOPort

with IOPort(Input(), Output()) as port:
    print('Using {} and {}'.format(port.inport, port.outport))
    port.send(mido.new('pitchwheel', pitch=122))
    for message in port:
        print('Received {}, sending it back out.'.format(message))
        port.send(message)
