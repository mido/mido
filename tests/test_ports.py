# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import itertools

import pytest

from mido import ports
from mido.messages import Message
from mido.ports import BaseInput, BaseIOPort, MultiPort


class TestIOPort:
    class Port(BaseIOPort):
        def _open(self):
            self.close_called = False

        def _send(self, message):
            self._messages.append(message)

        def _close(self):
            self.close_called = True

    @pytest.fixture
    def port(self):
        with self.Port('Name') as p:
            yield p

    def test_basic(self, port):
        assert port.name == 'Name'
        assert not port.closed
        assert port._messages is port._parser.messages

        with pytest.raises(TypeError):
            port.send('not a message')

    def test_recv_non_blocking(self, port):
        message = Message('note_on')

        port.send(message)
        port.poll()
        assert port.poll() is None

    def test_send_message(self, port):
        message = Message('note_on')

        port.send(message)
        port.send(message)

    def test_port_close(self, port):
        port.close()
        assert port.close_called
        port.close_called = False
        port.close()
        assert port.closed
        assert not port.close_called

    def test_mido_port_non_blocking_recv(self, port):
        assert port.receive(block=False) is None


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


@pytest.mark.parametrize('yield_ports', [False, True])
def test_multi_port_blocking_receive_returns_queued_message(monkeypatch,
                                                            yield_ports):
    source = BaseInput()
    message = Message('note_on', note=60)

    source._messages.append(message)

    def unexpected_sleep():
        pytest.fail('MultiPort should drain a queued message before waiting')

    monkeypatch.setattr(ports, 'sleep', unexpected_sleep)

    with source, MultiPort([source], yield_ports=yield_ports) as multi:
        received = multi.receive()

    if yield_ports:
        assert received[0] is source
        assert received[1] is message
    else:
        assert received is message


def test_multi_port_blocking_receive_waits_for_later_message(monkeypatch):
    source = BaseInput()
    message = Message('note_on', note=61)
    injected = False

    def inject_once():
        nonlocal injected
        if injected:
            pytest.fail('MultiPort kept waiting after receiving the message')
        injected = True
        source._messages.append(message)

    monkeypatch.setattr(ports, 'sleep', inject_once)

    with source, MultiPort([source]) as multi:
        assert multi.receive() is message

    assert injected


def test_multi_port_non_blocking_receive_returns_none_when_empty():
    source = BaseInput()

    with source, MultiPort([source]) as multi:
        assert multi.receive(block=False) is None


def test_multi_port_receive_stops_when_closed_while_waiting(monkeypatch):
    source = BaseInput()
    calls = 0

    def close_on_sleep():
        nonlocal calls
        calls += 1
        multi.close()
        if calls > 1:
            pytest.fail('MultiPort kept polling after it was closed')

    monkeypatch.setattr(ports, 'sleep', close_on_sleep)

    with source, MultiPort([source]) as multi:
        with pytest.raises(OSError, match='port closed during receive'):
            multi.receive()

    assert calls == 1


def test_multi_port_iteration_returns_pending_messages(monkeypatch):
    source = BaseInput()
    messages = [Message('note_on', note=62), Message('note_on', note=63)]
    source._messages.extend(messages)

    def unexpected_sleep():
        pytest.fail('MultiPort should return pending messages during iteration')

    monkeypatch.setattr(ports, 'sleep', unexpected_sleep)

    with source, MultiPort([source]) as multi:
        assert list(itertools.islice(multi, 2)) == messages
