# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from pytest import mark

from mido.tokenizer import Tokenizer


def tokenize(midi_bytes):
    return list(Tokenizer(midi_bytes))


def test_channel_message():
    assert tokenize([0x90, 1, 2]) == [[0x90, 1, 2]]


def test_sysex():
    assert tokenize([0xf0, 1, 2, 3, 0xf7]) == [[0xf0, 1, 2, 3, 0xf7]]


def test_empty_sysex():
    assert tokenize([0xf0, 0xf7]) == [[0xf0, 0xf7]]


def test_realtime():
    assert tokenize([0xf8]) == [[0xf8]]


def test_double_realtime():
    assert tokenize([0xf8, 0xf8]) == [[0xf8], [0xf8]]


@mark.parametrize('message', [
    [0x80, 60, 64], [0x90, 60, 64], [0xa0, 60, 64],
    [0xb0, 1, 64], [0xc0, 5], [0xd0, 64], [0xe0, 0, 64],
    [0xf1, 0], [0xf2, 0, 64], [0xf3, 5],
])
@mark.parametrize('realtime', range(0xf8, 0x100))
def test_realtime_inside_message(message, realtime):
    """Realtime bytes must not discard an interrupted channel/common message."""
    for split in range(1, len(message)):
        interrupted = message[:split] + [realtime] + message[split:]
        expected = [] if realtime in (0xf9, 0xfd) else [[realtime]]
        assert tokenize(interrupted) == expected + [message]


def test_realtime_inside_sysex():
    """Deliver realtime before completing the interrupted sysex message."""
    assert tokenize([0xf0, 1, 0xf8, 2, 0xf7]) == [[0xf8], [0xf0, 1, 2, 0xf7]]
    assert tokenize([0xf0, 0xf8, 0xf7]) == [[0xf8], [0xf0, 0xf7]]


def test_message_inside_sysex():
    """Non-realtime message inside sysex should reset the parser."""
    assert tokenize([0xf0, 0x90, 1, 2, 0xf7]) == [[0x90, 1, 2]]


def test_sysex_inside_sysex():
    """Sysex inside sysex should reset the parser."""
    assert tokenize([0xf0, 1, 0xf0, 2, 0xf7]) == [[0xf0, 2, 0xf7]]


def test_stray_data_bytes():
    """Data bytes outside messages should be ignored."""
    assert tokenize([0, 1, 0x90, 2, 3, 4, 5, 0xf8, 6]) == \
           [[0x90, 2, 3], [0xf8]]
