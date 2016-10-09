from collections import deque
from .msg.msg import Message
from .msg.decode import Decoder

# Todo: make sure the method signatures are as before.
# Todo: add doc strings.

class Parser:
    def __init__(self, data=None):
        self.messages = deque()
        self._decoder = Decoder(data)
        self._wrap_messages()

    def _wrap_messages(self):
        for msgdict in self._decoder:
            self.messages.append(Message.from_dict(msgdict))

    def feed(self, data):
        self._decoder.feed(data)
        self._wrap_messages()

    def feed_byte(self, byte):
        self._decoder.feed_byte(byte)
        self._wrap_messages()

    def get_message(self):
        if self.messages:
            return self.messages.popleft()
        else:
            return None

    def __iter__(self):
        while self.messages:
            yield self.get_message()

    def __len__(self):
        return len(self.messages)


def parse_all(data):
    return list(Parser(data))


def parse(data):
    return Parser(data).get_message()
