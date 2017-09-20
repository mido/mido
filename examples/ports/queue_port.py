"""A port interface around a queue.

This allows you to create internal ports to send messages between threads.
"""
import mido
from mido import ports

try:
    import queue
except ImportError:
    # Python 2.
    import Queue as queue


class QueuePort(ports.BaseIOPort):
    # We don't need locking since the queue takes care of that.
    _locking = False

    def _open(self):
        self.queue = queue.Queue()

    def _send(self, msg):
        self.queue.put(msg)

    def _receive(self, block=True):
        try:
            return self.queue.get(block=block)
        except queue.Empty:
            return None

    def _device_type(self):
        return 'Queue'


def main():
    msg = mido.Message('clock')

    port = QueuePort()
    print(port.poll())
    port.send(msg)
    print(port.receive())


if __name__ == '__main__':
    main()
