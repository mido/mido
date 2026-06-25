# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from pytest import raises

from mido.messages import Message


def test_decode_sysex():
    assert Message.from_str('sysex data=(1,2,3)').data == (1, 2, 3)


def test_decode_invalid_sysex_with_spaces():
    with raises(ValueError):
        Message.from_str('sysex data=(1, 2, 3)')


def test_encode_sysex():
    assert str(Message('sysex', data=())) == 'sysex data=() time=0'
    # This should not have an extra comma.
    assert str(Message('sysex', data=(1,))) == 'sysex data=(1) time=0'
    assert str(Message('sysex', data=(1, 2, 3))) == 'sysex data=(1,2,3) time=0'


def test_decode_empty_sysex():
    assert Message.from_str('sysex data=() time=0').data == ()


def test_sysex_str_roundtrip():
    for data in [(), (1,), (1, 2, 3)]:
        msg = Message('sysex', data=data)
        assert Message.from_str(str(msg)) == msg


def test_decode_sysex_missing_parens():
    with raises(ValueError, match='missing parentheses'):
        Message.from_str('sysex data=1,2,3 time=0')


def test_decode_sysex_missing_open_paren():
    with raises(ValueError, match='missing parentheses'):
        Message.from_str('sysex data=1,2,3) time=0')
