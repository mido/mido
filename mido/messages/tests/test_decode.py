from pytest import raises
from ..decode import decode_msg


def sysex(data):
    """Make sysex data."""
    return b'\xf0' + bytes(data) + b'\xf7'


def test_sysex():
    encoded = b'\xf0\x00\xf7'
    decoded = dict(type='sysex', data=b'\x00', time=0)
    assert decode_msg(encoded) == decoded


def test_channel():
    assert decode_msg(b'\x91\x00\x00')['channel'] == 1


def test_sysex_end():
    with raises(ValueError):
        decode_msg(b'\xf0\x00\x12')


def test_zero_bytes():
    with raises(ValueError):
        decode_msg(b'')


def test_too_few_bytes():
    with raises(ValueError):
        decode_msg(b'\x90')


def test_too_many_bytes():
    with raises(ValueError):
        decode_msg(b'\x90\x00\x00\x00')


def test_invalid_status():
    with raises(ValueError):
        decode_msg(b'\x00')
