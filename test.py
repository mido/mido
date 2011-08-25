#!/usr/bin/env python

import midi
import midi.portmidi as pm

pm.debug = True

with pm.context():
    out = pm.Output()
    out.send([1, 2, 3])


