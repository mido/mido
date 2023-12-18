# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT
from warnings import catch_warnings

from pytest import raises

from mido.protocol.version1.message.decode import decode_message


def sysex(data):
    """Make sysex data."""
    return [0xf0] + list(data) + [0xf7]


def test_sysex():
    data = b'\xf0\x01\x02\x03\xf7'
    msg = {'type': 'sysex', 'data': (1, 2, 3), 'timestamp': 0}
    assert decode_message(data) == msg


def test_channel():
    assert decode_message(b'\x91\x00\x00')['channel'] == 1


def test_sysex_end():
    with catch_warnings(record=True) as w:
        decode_message(b'\xf0\x00\x12')
        assert len(w) == 1


def test_zero_bytes():
    with raises(ValueError):
        decode_message(b'')


def test_too_few_bytes():
    with raises(ValueError):
        decode_message(b'\x90')


def test_too_many_bytes():
    with raises(ValueError):
        decode_message(b'\x90\x00\x00\x00')


def test_invalid_status():
    with raises(ValueError):
        decode_message(b'\x00')


def test_sysex_without_stop_byte():
    with catch_warnings(record=True) as w:
        decode_message([0xf0])
        assert len(w) == 1

    with catch_warnings(record=True) as w:
        decode_message([0xf0, 0])
        assert len(w) == 1
