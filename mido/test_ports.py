from pytest import raises
from .messages import Message
from .ports import BaseIOPort

def test_ioport():
    class Port(BaseIOPort):
        def _open(self):
            self.close_called = False

        def _send(self, message):
            self._messages.append(message)

        def _close(self):
            self.close_called = True

    with Port('Name') as port:
        assert port.name == 'Name'
        assert not port.closed

        assert port._messages is port._parser.messages

        with raises(TypeError): port.send('not a message')

    with Port('Name') as port:
        message = Message('note_on')

        # Receive a message. (Non-blocking.)
        port.send(message)
        _ = port.poll()
        assert port.poll() is None

    with Port('Name') as port:
        message = Message('note_on')

        port.send(message)
        port.send(message)

    with Port('Name') as port:
        port.close()
        assert port.close_called
        port.close_called = False
        port.close()
        assert port.closed
        assert not port.close_called


def test_close_inside_iteration():
    # This type of port can close when it runs out of messages.
    # (And example of this is socket ports.)
    #
    # Iteration should then stop after all messages in the
    # internal queue have been received.
    message = Message('note_on')

    class Port(BaseIOPort):
        def __init__(self, messages):
            BaseIOPort.__init__(self)
            # Simulate some messages that arrived
            # earlier.
            self._messages.extend(messages)
            self.closed = False

        def _receive(self, block=True):
            # Oops, the other end hung up.
            if self._messages:
                return self._messages.popleft()
            else:
                self.close()
                return None

    message = Message('note_on')
    with Port([message, message]) as port:
        assert len(list(port)) == 2
