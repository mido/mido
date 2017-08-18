import time
from .. import ports
from ..parser import Parser
from ..py2 import PY2

from threading import RLock

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

    q.put(msg)
    q.put_bytes([0xf8, 0, 0])

    msg = q.get()
    msg = q.poll()
    """
    def __init__(self):
        self._queue = queue.Queue()
        self._parser = Parser()
        self._parser_lock = RLock()

    def put(self, msg):
        self._queue.put(msg)

    def put_bytes(self, msg_bytes):
        with self._parser_lock:
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

    # TODO: add timeout?
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

    def __iter__(self):
        while True:
            return self.get()

    def iterpoll(self):
        while True:
            msg = self.poll()
            if msg is None:
                return
            else:
                yield msg
