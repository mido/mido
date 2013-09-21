#!/usr/bin/env python
from mido import Message
from mido.ports import BaseInput, BaseOutput

class BufferPort(BaseInput, BaseOutput):
    def _send(self, message):
        self._messages.append(message)

    def _get_device_type(self):
        return 'buffer'

    # Make sure we never need to wait.
    __iter__ = BaseInput.iter_pending

if __name__ == '__main__':
    buffer = BufferPort()

    buffer.send(Message('program_change', program=7))
    buffer.send(Message('control_change', control=1, value=2))
    for message in buffer:
        print(message)

    buffer.send(Message('control_change', control=2, value=3))
    print list(buffer)
