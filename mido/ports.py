"""
Utility functions for dealing with ports.

Module content:

    multi_receive(*ports)
"""

import time
import random

def multi_receive(ports):
    """Receive messages from multiple ports.

    Generates (message, port) tuples from every port in ports. The
    ports are polled in random order for fairness, and all messages
    from each port are yielded before moving on to the next port.
    """
    ports = list(ports)
    while 1:
        random.shuffle(ports)
        
        for port in ports:
            for _ in range(port.pending()):
                yield (port.receive(), port)

        time.sleep(0.001)

