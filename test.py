#!/usr/bin/env python3

from modo import parse
from modo.msg import *

msg = Message('note_on', channel=1, note=2, velocity=3)
msg = Message('note_on')
msg = Message(0x96)

print(parse((a for a in [0x81, 2, 3])))
print(parse(b'\x81\x01\x02'))
print(parse([0xf0, 0x10, 0x20, 0xf7, 0x96, 0xfb, 0x01, 0x02]))

print(note_on(1, 2, 3))
print(note_on(2, 3, 4))
