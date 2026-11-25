# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from pytest import mark, raises

from mido.messages import Message, parse_string, parse_string_stream


@mark.parametrize('text', ['', ' \t\n ', 'not_a_message'])
def test_invalid_message_string(text):
    with raises(ValueError):
        Message.from_str(text)
    with raises(ValueError):
        parse_string(text)


def test_string_stream_recovers_from_unknown_message_type():
    results = list(parse_string_stream([
        'note_on note=60',
        '# comment',
        'not_a_message',
        '',
        'note_off note=60',
    ]))
    assert results[0] == (Message('note_on', note=60), None)
    assert results[1][0] is None
    assert results[1][1].startswith('line 3: ')
    assert 'not_a_message' in results[1][1]
    assert results[2] == (Message('note_off', note=60), None)


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
