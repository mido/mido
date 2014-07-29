"""
Useful tools for working with ports

Module content:

    multi_receive -- receive messages from multiple ports
    multi_iter_pending -- iterate through messages from multiple ports
    IOPort -- combined input / output port. Wraps around to normal ports
    MessageBuffer -- pseudo-port that stores messages in a deque
"""

from __future__ import unicode_literals
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

    This is used in ports when polling and waiting for messages. N can
    be set with set_sleep_time()."""
    time.sleep(_sleep_time)

def set_sleep_time(seconds=_DEFAULT_SLEEP_TIME):
    """Set the number of seconds sleep() will sleep."""
    global _sleep_time
    _sleep_time = seconds

def get_sleep_time():
    """Get number of seconds sleep() will sleep."""
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

    def _send(self, message):
        pass

    def _receive(self, block=True):
        pass

    def close(self):
        """Close the port.

        If the port is already closed, nothing will happen.  The port
        is automatically closed when the object goes out of scope or
        is garbage collected.
        """
        if not self.closed:
            if hasattr(self, 'autoreset') and self.autoreset:
                try:
                    self.reset()
                except IOError:
                    pass

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

        capabilities = (hasattr(self, 'receive'), hasattr(self, 'send'))
        port_type = {
            (True, False): 'input',
            (False, True): 'output',
            (True, True): 'I/O',
            (False, False): 'mute',
            }[capabilities]

        name = self.name or ''

        try:
            device_type = self._device_type
        except AttributeError:
            device_type = self.__class__.__name__

        return '<{} {} {!r} ({})>'.format(
            state, port_type, name, device_type)


class BaseInput(BasePort):
    """
    Base class for input port.

    Override _pending() to create a new input port type.
    (See portmidi.py for an example of how to do this.)
    """

    def __init__(self, name='', **kwargs):
        """Create an input port.

        name is the port name, as returned by input_names(). If
        name is not passed, the default input is used instead.
        """
        self.callback = kwargs.get('callback')
        self._parser = Parser()
        self._messages = self._parser._parsed_messages  # Shortcut.
        BasePort.__init__(self, name, **kwargs)

    def pending(self):
        """Return how many messages are ready to be received.

        This will read data from the device and put it in the
        parser. I will then return the number of messages available to
        be received.

        If this is called on a closed port it will work as normal
        except it won't try to read from the device.
        """
        if not self.closed:
            self._receive(block=False)

        return len(self._messages)

    def iter_pending(self):
        """Iterate through pending messages."""
        self._receive(block=False)
        while self._messages:
            yield self._messages.popleft()

    def receive(self, block=True):
        """Return the next message.

        This will block until a message arrives. For non-blocking
        behavior, you can use pending() to see how many messages can
        safely be received without blocking.

        If the port is closed and there are no pending messages, IOError
        will be raised. If the port closes while waiting inside receive(),
        IOError will be raised. Todo: this seems a bit inconsistent. Should
        different errors be raised? What's most useful here?

        If block=False is passed, None will be returned if there are no
        pending messages or if the port is closed.
        """
        if self.callback:
            raise IOError('a callback is currently set for this port')

        # If there is a message pending, return it right away.
        if self._messages:
            return self._messages.popleft()

        if self.closed:
            if block:
                raise IOError('receive() called on closed port')
            else:
                return None

        while 1:
            self._receive(block=block)
            if self._messages:
                return self._messages.popleft()
            elif not block:
                return None
            elif self.closed:
                raise IOError('port closed during receive()')

            sleep()

    def __iter__(self):
        """Iterate through messages until the port closes."""
        # This could have simply called receive() in a loop, but that
        # could result in a "port closed during receive()" error which
        # is hard to catch here.
        while 1:
            try:
                yield self.receive()
            except IOError:
                if self.closed:
                    # The port closed before or inside receive().
                    # (This makes the assumption that this is the reason,
                    # at the risk of masking other errors.)
                    return
                else:
                    raise

class BaseOutput(BasePort):
    """
    Base class for output port.

    Subclass and override _send() to create a new port type.  (See
    portmidi.py for how to do this.)
    """

    def __init__(self, name='', autoreset=False, **kwargs):
        """Create an output port
        
        name is the port name, as returned by output_names(). If
        name is not passed, the default output is used instead.
        """
        BasePort.__init__(self, name, **kwargs)
        self.autoreset = autoreset

    def send(self, message):
        """Send a message on the port.

        A copy of the message will be sent, so you can safely modify
        the original message without any unexpected consequences.
        """
        if not isinstance(message, Message):
            raise TypeError('argument to send() must be a Message')
        elif self.closed:
            raise ValueError('send() called on closed port')

        self._send(message.copy())

    def reset(self):
        """Send "All Notes Off" and "Reset All Controllers" on all channels
        """
        if self.closed:
            return

        ALL_NOTES_OFF = 123
        RESET_ALL_CONTROLLERS = 121
        for channel in range(16):
            for control in [ALL_NOTES_OFF, RESET_ALL_CONTROLLERS]:
                self.send(Message('control_change',
                                  channel=channel,
                                  control=control))

    def panic(self):
        """Send "All Sounds Off" on all channels.

        This will mute all sounding notes regardless of
        envelopes. Useful when notes are hanging and nothing else
        helps.
        """
        if self.closed:
            return

        ALL_SOUNDS_OFF = 120
        for channel in range(16):
            self.send(Message('control_change',
                              channel=channel,
                              control=ALL_SOUNDS_OFF))

class BaseIOPort(BaseInput, BaseOutput):
    pass

class IOPort(BaseIOPort):
    """Input / output port.

    This is a convenient wrapper around an input port and an output
    port which provides the functionality of both. Every method call
    is forwarded to the appropriate port.
    """

    def __init__(self, input, output):
        self.input = input
        self.output = output

        # We use str() here in case name is None.
        self.name = '{} + {}'.format(str(input.name), str(output.name))
        self._messages = self.input._messages
        self.closed = False

    def _close(self):
        self.input.close()
        self.output.close()

    def _send(self, message):
        self.output._send(message)

    def _receive(self, block=True):
        return self.input._receive()


class EchoPort(BaseIOPort):
    def _send(self, message):
        self._messages.append(message)

    __iter__ = BaseIOPort.iter_pending


# Todo: i don't know how to implement yield_ports here, so for now I haven't.
class MultiPort(BaseIOPort):
    def __init__(self, ports):
        BaseIOPort.__init__(self, 'multi')
        self.ports = ports

    def _send(self, message):
        for port in self.ports:
            if not port.closed:
                # Todo: what if a SocketPort connection closes in-between here?
                port.send(message)

    def _receive(self, block=True):
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
