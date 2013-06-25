"""
List portmidi devices.
"""

from __future__ import print_function

import mido.portmidi as pm

print('Input ports:')
for name in pm.get_input_names():
    print('   ', repr(name))
print()

print('Output ports:')
for name in pm.get_output_names():
    print('   ', repr(name))
print()
