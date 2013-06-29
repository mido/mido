"""
Utility functions for dealing with ports.

Module content:

    multi_receive(ports) -> Message generator
    multi_iter_pending(ports) -> Message generator
    IOPort
    MessageBuffer
"""

import time
import random
from collections import deque

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


def multi_iter_pending(ports):
    """Iterate through all pending messages in ports.

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


class IOPort(object):
    """Input / output port.

    This is a convenient wrapper around an input port and
    and an output port which provides the functionality of
    both. Every method call is forwarded to the appropriate
    port.

    I don't know if it works yet.
    """

    def __init__(self, inport, outport):
        self.inport = inport
        self.outport = outport
        self.closed = False

        # Todo: what if they have different names?
        self.name = self.inport.name

    def send(self, message):
        return self.outport.send(message)

    def receive(self):
        return self.inport.receive()

    def pending(self):
        return self.inport.pending()

    def close(self):
        if not self.closed:
            self.inport.close()
            self.outport.close()

    def __iter__(self):
        for message in self.inport:
            yield message

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        return "<{} I/O port '{}'>".format(state, self.name)


class MessageBuffer:
    """
    Maintains an internal deque of messages.

    This can be used in place of an output port to buffer up messages
    by calling send(), and then later get them out with get_message()
    or 'for message in buffer:'.

    receive() is not supported, because it would be a bad idea for a
    MessageBuffer object to block, since it's getting its data from
    the same thread as the one it's running in.

    I don't know if it works yet.
    """

    def __init__(self):
        self.messages = deque()

    def put_message(self, message):
        """Store one message in the buffer."""
        self.messages.append(message)
        
    def get_message(self):
        """Get the first message in the buffer."""
        if self.messages:
            self.messages.popleft()
        else:
            return None

    def clear(self):
        """Remove all messages from the buffer."""

    def send(self, message):
        """Store one message in the buffer.

        This is an alias for put_message() to make the buffer behave
        like an output port."""
        self.messages.append(message)

    def pending(self):
        """Return number of messages in the buffer."""
        return len(self.messages)

    def __len__(self):
        """Return number of messages in the buffer.

        This is an alias for pending()."""
        return len(self.messages)

    def __iter__(self):
        while self.messages:
            yield self.messages.popleft()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        return False
