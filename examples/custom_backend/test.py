import time
import mido

mido.set_backend('printer')

print('Available outputs: {}'.format(mido.get_output_names()))

with mido.open_output() as port:
    print('Using {}.'.format(port))

    port.send(mido.Message('program_change', program=10))
    for i in [1, 2, 3]:
        port.send(mido.Message('control_change', control=1, value=i))
