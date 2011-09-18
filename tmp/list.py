#!/usr/bin/env python

"""
List portmidi devices.
"""

import pprint
import protomidi.portmidi as pm

pprint.pprint(pm.get_devinfo())
