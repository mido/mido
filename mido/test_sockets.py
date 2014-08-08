from pytest import raises
from .sockets import parse_address

def test_parse_address():
    assert parse_address(':8080') == ('', 8080)
    assert parse_address('localhost:8080') == ('localhost', 8080)

    with raises(ValueError): parse_address(':to_many_colons:8080')
    with raises(ValueError): parse_address('only_hostname')
    with raises(ValueError): parse_address('')
    with raises(ValueError): parse_address(':')
    with raises(ValueError): parse_address(':shoe')
    with raises(ValueError): parse_address(':0')
    with raises(ValueError): parse_address(':65536')  # Out of range.
