import time
import random
import mido
from mido.sockets import SocketPort

with SocketPort('localhost', 8080) as port:
    while 1:
        port.send(mido.Message('program_change',
                               program=random.randrange(128)))

        time.sleep(0.2)
