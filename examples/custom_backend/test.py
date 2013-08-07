"""
Try out the new printer port backend.

It also works with MIDO_BACKEND, so you can do:

    $ MIDO_BACKEND=printer python
    >>> import mido
    >>> mido.get_output_names()
    ['The Printer Port']
"""

import time
import mido

mido.set_backend('printer')

print('Available outputs: {!r}'.format(mido.get_output_names()))

with mido.open_output() as port:
    print('Using {}.'.format(port))

    port.send(mido.Message('program_change', program=10))
    for i in [1, 2, 3]:
        port.send(mido.Message('control_change', control=1, value=i))
