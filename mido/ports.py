"""
Utility functions for dealing with ports.

Module content:

    multi_receive(*ports)
"""

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
            for _ in range(port.poll()):
                yield (port.receive(), port)
