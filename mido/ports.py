"""
Utility functions for dealing with ports.

The functions in here are experimental, but they may become a part of
the library in there future.
"""

import time
import random

def receive_from_ports(ports):
    """Receive messages from multiple ports.

    Note: This function should be considered experimental.
    It can go away or change in there future.

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

def iterate_pending_at_ports(ports):
    """Iterate through all pending messages in ports.

    Note: This function should be considered experimental for now.
    It can go away or change in there future.

    ports is an iterable of message ports to check.

    Yields (message, port) tuples until there are no more pending
    messages. This can be used to receive messages from
    a set of ports in a non-blocking manner.
    """
    ports = list(ports)
    random.shuffle(ports)
    for port in ports:
        for _ in range(port.pending()):
            yield (port.receive(), port)
