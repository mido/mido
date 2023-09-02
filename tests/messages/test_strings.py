# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from pytest import raises

from mido.protocol.version1.message import Message


def test_decode_sysex():
    assert Message.from_str('sysex data=(1,2,3)').data == (1, 2, 3)


def test_decode_invalid_sysex_with_spaces():
    with raises(ValueError):
        Message.from_str('sysex data=(1, 2, 3)')


def test_encode_sysex():
    assert str(Message('sysex', data=())) == 'sysex data=() timestamp=0'
    # This should not have an extra comma.
    assert str(Message('sysex', data=(1,))) == 'sysex data=(1) timestamp=0'
    assert str(Message('sysex', data=(1, 2, 3))) == (
        'sysex data=(1,2,3) timestamp=0')
