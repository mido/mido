# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import pytest

from mido.sockets import PortServer, connect, format_address, parse_address


class TestSocketPortNames:
    """Socket ports are named after their address.

    See issues #683 (format_address() drops the ':' between host and
    port, and PortServer never applies the formatted address as its
    name).
    """

    def test_format_address(self):
        assert format_address('localhost', 8080) == 'localhost:8080'

    def test_format_address_round_trip(self):
        assert parse_address(format_address('localhost', 8080)) == \
            ('localhost', 8080)

    def test_port_server_name(self):
        with PortServer('localhost', 0) as server:
            assert server.name == 'localhost:0'

    def test_client_name(self):
        with PortServer('localhost', 0) as server:
            portno = server._socket.getsockname()[1]
            with connect('localhost', portno) as client:
                assert client.name == f'localhost:{portno}'



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
