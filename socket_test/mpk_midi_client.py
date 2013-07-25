import time
import random
import mido
from mido.sockets import SocketPort

with SocketPort('192.168.1.101', 8080) as port:
    with mido.open_input('MPK mini MIDI 1') as mpk:
        for message in mpk:
            port.send(message)
