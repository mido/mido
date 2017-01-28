"""
These classes will be made publicly available once their API is settled. For now they should only be used
inside this package.
"""
import time
from .. import ports
from ..parser import Parser
from ..py2 import PY2

if PY2:
    import Queue as queue
else:
    import queue


class ParserQueue:
    """
    Thread safe message queue with built in MIDI parser.

    This should be avaiable to other backend implementations and perhaps
    also in the public API, but the API needs a bit of review. (Ideally This
    would replace the parser.)

    q = ParserQueue()

    q.feed([0xf8, 0, 0])
    q.put(msg)

    msg = q.get()
    msg = q.poll()
    for msg in q:
        ...
    """
    def __init__(self):
        self._queue = queue.Queue()
        self._parser = Parser()

    def put(self, msg):
        self._queue.put(msg)

    def feed(self, msg_bytes):
        # Todo: should this be protected somehow?
        # No, it's better to put a lock around reading AND parsing.
        self._parser.feed(msg_bytes)
        for msg in self._parser:
            self.put(msg)

    def _get_py2(self):
        # In Python 2 queue.get() doesn't respond to CTRL-C. A workaroud is
        # to call queue.get(timeout=100) (very high timeout) in a loop, but all
        # that does is poll with a timeout of 50 milliseconds. This results in
        # much too high latency.
        #
        # It's better to do our own polling with a shorter sleep time.
        #
        # See Issue #49 and https://bugs.python.org/issue8844
        sleep_time = ports.get_sleep_time()
        while True:
            try:
                return self._queue.get_nowait()
            except queue.Empty:
                time.sleep(sleep_time)
                continue

    # Todo: add timeout?
    def get(self):
        if PY2:
            return self._get_py2()
        else:
            return self._queue.get()

    def poll(self):
        try:
            return self._queue.get_nowait()
        except queue.Empty:
            return None

    def iterpoll(self):
        while True:
            msg = self.poll()
            if msg:
                yield msg
            else:
                return


class PortMethods(object):
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

        capabilities = self.is_input, self.is_output
        port_type = {
            (True, False): 'input',
            (False, True): 'output',
            (True, True): 'I/O port',
            (False, False): 'mute port',
            }[capabilities]

        name = self.name or ''

        try:
            device_type = self._device_type
        except AttributeError:
            device_type = self.__class__.__name__

        return '<{} {} {!r} ({})>'.format(
            state, port_type, name, device_type)


class InputMethods(object):

    def iter_pending(self):
        """Iterate through pending messages."""
        while True:
            msg = self.poll()
            if msg is None:
                return
            else:
                yield msg

    def __iter__(self):
        """Iterate through messages until the port closes."""
        while True:
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


class OutputMethods(object):
    def reset(self):
        """Send "All Notes Off" and "Reset All Controllers" on all channels"""
        for msg in ports.reset_messages():
            self.send(msg)

    def panic(self):
        """Send "All Sounds Off" on all channels.

        This will mute all sounding notes regardless of
        envelopes. Useful when notes are hanging and nothing else
        helps.
        """
        for msg in ports.panic_messages():
            self.send(msg)
