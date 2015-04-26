#!/usr/bin/env python
"""
Queue port for threading.
"""

import sys
PY2 = (sys.version_info.major == 2)

if PY2:
    from Queue import Queue, Empty
else:
    from queue import Queue, Empty
from threading import Thread
import time
import random

from mido import Message
from mido.ports import BaseInput, BaseOutput

PY2 = (sys.version_info.major == 2)

class QueuePort(BaseInput, BaseOutput):
    def _open(self, **kwargs):
        maxsize = kwargs.get('maxsize', 0)
        self._queue = Queue(maxsize)

    def _send(self, message):
        self._queue.put(message)

    def _receive(self, block=True):
        while True:
            try:
                message = self._queue.get_nowait()
            except Empty:
                return
            else:
                self._messages.append(message)
    
    def _get_device_type(self):
        return 'queue'
    
if __name__ == '__main__':
    def program_changer():
        while True:
            queue_port.send(
                Message('program_change', program=random.randrange(128)))
            time.sleep(0.2)

    queue_port = QueuePort(maxsize=3)

    thread = Thread(target=program_changer)
    thread.daemon = True
    thread.start()

    for message in queue_port:
        print(message)
