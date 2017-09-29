import pytest
from mido.sockets import parse_address


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
