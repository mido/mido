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

# How many seconds to sleep before polling again.
_DEFAULT_SLEEP_TIME = 0.001
_sleep_time = _DEFAULT_SLEEP_TIME

# Todo: document this more.
def sleep():
    """Sleep for N seconds.

    N can be accessed with set_sleep_time() and get_sleep_time()."""
    time.sleep(_sleep_time)

def set_sleep_time(seconds=_DEFAULT_SLEEP_TIME):
    global _sleep_time
    _sleep_time = seconds

def get_sleep_time():
    return _sleep_time

class BasePort(object):
    """
    Abstract base class for Input and Output ports.
    """

    def __init__(self, name=None, **kwargs):
        self.name = name
        self.closed = True
        self._open(**kwargs)
        self.closed = False

    def _open(self, **kwargs):
        pass

    def _close(self):
        pass

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
        return False

    def __repr__(self):
        if self.closed:
            state = 'closed'
        else:
            state = 'open'

        capabilities = (hasattr(self, 'receive'), hasattr(self, 'send'))
        port_type = {
            (True, False): 'input',
            (False, True): 'output',
            (True, True): 'I/O',
            (False, False): 'mute',
            }[capabilities]

        device_name = self._get_device_type()

        return "<{state} {port_type} port '{self.name}'" \
               " ({device_name})>".format(**locals())


class BaseInput(BasePort):
    """
    Base class for input port.

    Override _pending() to create a new input port type.
    (See portmidi.py for an example of how to do this.)
    """

    def __init__(self, name=None, **kwargs):
        """Create an input port.

        name is the port name, as returned by input_names(). If
        name is not passed, the default input is used instead.
        """
        self._parser = Parser()
        self._messages = self._parser._parsed_messages  # Shortcut.
        BasePort.__init__(self, name, **kwargs)

    def _pending(self):
        return None

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
            return len(self._messages)
        else:
            num_messages = self._pending()
            if num_messages is None:
                return len(self._messages)
            else:
                return num_messages

    def iter_pending(self):
        """Iterate through pending messages."""
        for _ in range(self.pending()):
            yield self._messages.popleft()

    def receive(self, block=True):
        """Return the next message.

        This will block until a message arrives. For non-blocking
        behavior, you can use pending() to see how many messages can
        safely be received without blocking.

        If the port is closed and there are no pending messages, ValueError
        will be raised. If the port closes while waiting inside receive(),
        IOError will be raised. Todo: this seems a bit inconsistent. Should
        different errors be raised? What's most useful here?

        If block=False is passed, None will be returned if there are no
        pending messages or if the port is closed.
        """
        # If there is a message pending, return it right away.
        if self._messages:
            return self._messages.popleft()
            
        if self.closed:
            if block:
                # Todo: which error?
                raise ValueError('receive() called on closed port')
            else:
                return None

        while 1:
            if self.pending():
                return self._messages.popleft()
            elif not block:
                return None
            elif self.closed:
                raise ValueError('port closed inside receive()')
            sleep()

    def __iter__(self):
        """Iterate through messages until the port closes."""
        while 1:
            for message in self.iter_pending():
                yield message
            if self.closed:
                return
            sleep()

class BaseOutput(BasePort):
    """
    Base class for output port.

    Subclass and override _send() to create a new port type.  (See
    portmidi.py for how to do this.)
    """

    def __init__(self, name=None, **kwargs):
        """Create an output port
        
        name is the port name, as returned by output_names(). If
        name is not passed, the default output is used instead.
        """
        BasePort.__init__(self, name, **kwargs)

    def _send(self, message):
        pass

    def send(self, message):
        """Send a message on the port.

        The message is sent immediately."""
        if not isinstance(message, Message):
            raise ValueError('argument to send() must be a Message')

        if self.closed:
            raise ValueError('send() called on closed port')

        self._send(message)

    def reset(self):
        """Send "All Notes Off" and "Reset All Controllers" on all channels
        """
        ALL_NOTES_OFF = 123
        RESET_ALL_CONTROLLERS = 121
        message = Message('control_change')
        for message.channel in range(16):
            for message.control in [ALL_NOTES_OFF, RESET_ALL_CONTROLLERS]:
                self.send(message)

    def panic(self):
        """Send "All Sounds Off" on all channels.

        Useful when notes are hanging, and nothing else helps.
        """
        ALL_SOUNDS_OFF = 120
        message = Message('control_change', control=ALL_SOUNDS_OFF)
        for message.channel in range(16):
            self.send(message)

class BaseIOPort(BaseInput, BaseOutput):
    pass

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

    def reset(self):
        return self.output.reset()
    send.__doc__ = BaseOutput.reset.__doc__

    def panic(self):
        return self.output.panic()
    panic.__doc__ = BaseOutput.panic.__doc__

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


class EchoPort(BaseIOPort):
    def _open(self):
        if self.name is None:
            self.name = 'echo'

    def _get_device_type(self):
        return 'echo'

    def _send(self, message):
        self._messages.append(message)

    def _pending(self):
        pass

    __iter__ = BaseIOPort.iter_pending


# Todo: i don't know how to implement yield_ports here, so for now I haven't.
class MultiPort(BaseIOPort):
    def __init__(self, ports):
        BaseIO.__init__(self, 'multi')
        self.ports = ports

    def _get_device_type(self):
        return 'multi'

    def _send(self, message):
        for port in self.ports:
            if not port.closed:
                # Todo: what if a SocketPort connection closes in-between here?
                port.send(message)

    def _pending(self):
        ports = list(self.ports)
        random.shuffle(ports)
        for port in ports:
            if not port.closed:
                for message in port.iter_pending():
                    self._messages.append(message)


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

        sleep()


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
