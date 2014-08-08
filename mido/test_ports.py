from pytest import raises
from .messages import Message
from .ports import BaseIOPort

def test_base_ioport():
    class Port(BaseIOPort):
        def _open(self):
            self.test_value = True

        def _send(self, message):
            self._messages.append(message)

        def _close(self):
            self.test_value = False

    with Port('Name') as port:
        assert port.name == 'Name'
        assert not port.closed

        assert port._messages is port._parser._parsed_messages

        with raises(TypeError): port.send('not a message')

        # Send message.
        message = Message('note_on')
        port.send(message)

        # Receive a message. (Blocking.)
        assert isinstance(port.receive(), Message)

        # Receive a message. (Non-blocking.)
        port.send(message)
        assert isinstance(port.receive(block=False), Message)
        assert port.receive(block=False) is None

        port.send(message)
        port.send(message)
        assert port.pending() == 2
        assert list(port.iter_pending()) == [message, message]

        # Todo: should this type of port close (and/or stop iteration)
        # when there are no messages?
        # port.send(message)
        # port.send(message)
        # assert port.pending() == 2
        # assert list(port) == [message, message]

    assert port.closed

def test_non_finite_port():
    # This type of port can close when it runs out of messages.
    # (And example of this is socket ports.)
    #
    # Iteration should then stop after all messages in the
    # internal queue have been received.
    message = Message('note_on')

    class Port(BaseIOPort):
        def _open(self):
            # Simulate some messages that arrived
            # earlier.
            self._messages.extend([message, message])

        def _receive(self, block=True):
            # Oops, the other end hung up.
            self.close()

    with Port() as port:
        assert len(list(port)) == 2
