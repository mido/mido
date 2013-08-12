"""
Useful tools for working with ports

Module content:

    multi_receive -- receive messages from multiple ports
    multi_iter_pending -- iterate through messages from multiple ports
    IOPort -- combined input / output port. Wraps around to normal ports
    MessageBuffer -- pseudo-port that stores messages in a deque
"""

import time
import random
from collections import deque
from .parser import Parser
from .messages import Message

class BasePort(object):
    """
    Abstract base class for Input and Output ports.
    """

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.closed = True
        self._open(**kwargs)
        self.closed = False
        self._parser = Parser()

    def _open(self, **kwargs):
        raise ValueError('_open() not implemented')

    def _close(self):
        raise ValueError('_close() not implemented')

    def _get_device_type(self):
        return 'Unknown'

    def close(self):
        """Close the port.

        If the port is already closed, nothing will happen.  The port
        is automatically closed when the object goes out of scope or
        is garbage collected.
        """
        if not self.closed:
            self._close()
            self.closed = True

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        if isinstance(self, BaseInput):
            port_type = 'input'
        elif isinstance(self, BaseOutput):
            port_type = 'output'
        else:
            port_type = 'I/O'  # Todo: this is wrong

        device_name = self._get_device_type()

        return "<{state} {port_type} port '{self.name}'" \
               " ({device_name})>".format(**locals())


class BaseInput(BasePort):
    """
    Base class for input port.

    Override _pending() to create a new input port type.
    (See portmidi.py for an example of how to do this.)
    """

    def __init__(self, name=None):
        """Create an input port.

        name is the port name, as returned by input_names(). If
        name is not passed, the default input is used instead.
        """
        self._parser = Parser()
        BasePort.__init__(self, name)

    def pending(self):
        """Return how many messages are ready to be received.

        This can be used for non-blocking receive(), for example:

             for _ in range(port.pending()):
                 message = port.receive()

        If this is called on a closed port, it will work as if
        the port was opened, but no new messages will be returned
        once the buffered ones run out.
        """
        if self.closed:
            return self._parser.pending()
        else:
            return self._pending()

    def iter_pending(self):
        """Iterate through pending messages."""
        for _ in range(self.pending()):
            yield self.receive()

    def receive(self):
        """Return the next message.

        This will block until a message arrives. For non-blocking
        behavior, you can use pending() to see how many messages can
        safely be received without blocking.
                
        NOTE: Blocking is currently implemented with polling and
        time.sleep(). This is inefficient, but the proper way doesn't
        work yet, so it's better than nothing.

        Todo: What should happen when the port is closed?
        - raise exception?
        - return pending messages until we run out, then raise exception?
        """
        # If there is a message pending, return it right away.
        message = self._parser.get_message()
        if message:
            return message

        if self.closed:
            raise ValueError('receive() called on closed port')

        # Wait for a message to arrive.
        while 1:
            time.sleep(0.001)
            if self.pending():
                # pending() has read at least one message from the
                # device. Return the first message.
                return self._parser.get_message()

    def __iter__(self):
        """Iterate through messages as they arrive on the port."""
        while 1:
            yield self.receive()

class BaseOutput(BasePort):
    """
    Base class for output port.

    Subclass and override _send() to create a new port type.  (See
    portmidi.py for how to do this.)
    """

    def __init__(self, name=None):
        """Create an output port
        
        name is the port name, as returned by output_names(). If
        name is not passed, the default output is used instead.
        """
        BasePort.__init__(self, name)

    def _send(self, message):
        raise ValueError('_send() is not implemented')

    def send(self, message):
        """Send a message on the port.

        The message is sent immediately."""
        if not isinstance(message, Message):
            raise ValueError('argument to send() must be a Message')

        if self.closed:
            raise ValueError('send() called on closed port')

        self._send(message)

class IOPort(object):
    """Input / output port.

    This is a convenient wrapper around an input port and an output
    port which provides the functionality of both. Every method call
    is forwarded to the appropriate port.
    """

    def __init__(self, input, output):
        self.input = input
        self.output = output
        self.closed = False

        # Todo: what if they have different names?
        self.name = self.input.name

    def close(self):
        if not self.closed:
            self.input.close()
            self.output.close()
            self.closed = True
    close.__doc__ = BasePort.close.__doc__

    def send(self, message):
        return self.output.send(message)
    send.__doc__ = BaseOutput.send.__doc__

    def receive(self):
        return self.input.receive()
    receive.__doc__ = BaseInput.receive.__doc__

    def pending(self):
        return self.input.pending()
    pending.__doc__ = BaseInput.pending.__doc__

    def iter_pending(self):
        for message in self.input.iter_pending():
            yield message
    iter_pending.__doc__ = BaseInput.iter_pending.__doc__

    def __iter__(self):
        for message in self.input:
            yield message

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        return "<{} I/O port '{}' ({})>".format(
            state, self.name, self.input._get_device_type())


def multi_receive(ports, yield_ports=False):
    """Receive messages from multiple ports.

    Generates messages from ever input port. The ports are polled in
    random order for fairness, and all messages from each port are
    yielded before moving on to the next port.
    
    If yield_ports=True, (port, message) is yielded instead of just
    the message.
    """
    ports = list(ports)
    while 1:
        random.shuffle(ports)
        
        for port in ports:
            for message in port.iter_pending():
                if yield_ports:
                    yield (port, message)
                else:
                    yield message

        time.sleep(0.001)


def multi_iter_pending(ports, yield_ports=False):
    """Iterate through all pending messages in ports.

    ports is an iterable of message ports to check.

    This can be used to receive messages from a set of ports in a
    non-blocking manner.

    If yield_ports=True, (port, message) is yielded instead of just
    the message.
    """
    ports = list(ports)
    random.shuffle(ports)
    for port in ports:
        for message in port.iter_pending():
            if yield_ports:
                yield (port, message)
            else:
                yield message
