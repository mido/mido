# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import time

import pytest

from mido import Message, ports
from mido.sockets import PortServer, connect, parse_address


class TestParseAddress:
    @pytest.mark.parametrize('input_str, expected',
                             [(':8080', ('', 8080)),
                              ('localhost:8080', ('localhost', 8080))
                              ])
    def test_parse_address_normal(self, input_str, expected):
        assert parse_address(input_str) == expected

    def test_too_many_colons_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address(':to_many_colons:8080')

    def test_only_hostname_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address('only_hostname')

    def test_empty_string_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address('')

    def test_only_colon_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address(':')

    def test_non_number_port_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address(':shoe')

    def test_port_zero_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address(':0')

    def test_out_of_range_port_raises_value_error(self):
        with pytest.raises(ValueError):
            parse_address(':65536')


def test_port_server_receives_message_from_connected_port(monkeypatch):
    message = Message('note_on', note=60)
    original_sleep = ports.sleep
    deadline = time.monotonic() + 1

    def sleep_until_deadline():
        if time.monotonic() >= deadline:
            pytest.fail('PortServer did not receive a message before the deadline')
        original_sleep()

    monkeypatch.setattr(ports, 'sleep', sleep_until_deadline)

    with PortServer('localhost', 0) as server:
        portno = server._socket.getsockname()[1]
        with connect('localhost', portno) as client:
            client.send(message)
            assert server.receive() == message
