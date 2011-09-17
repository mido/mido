#!/usr/bin/env python

from __future__ import print_function

import time
import pprint
import protomidi
from protomidi.msg import *
import protomidi.portmidi as io

pprint.pprint(io.get_devinfo())

# p = protomidi.Parser()
# p.feed('\x90\x01\x02')
# print p._messages

#print '('

i = io.Input()
while 1:
    if i.poll():
        msg = i.recv()
        print('   got:', msg)
    time.sleep(0.01)

# o = io.Output()
#print ')'
