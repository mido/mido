# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from pytest import raises

from mido.messages.checks import check_time


def test_check_time():
    check_time(1)
    check_time(1.5)

    with raises(TypeError):
        check_time(None)

    with raises(TypeError):
        check_time('abc')

    with raises(TypeError):
        check_time(None)

    with raises(TypeError):
        check_time('abc')


import pytest

from mido import Message


def test_message_rejects_values_outside_midi_spec_ranges():
    assert Message('note_on', channel=15, note=127, velocity=127).channel == 15
    assert Message('pitchwheel', pitch=-8192).pitch == -8192
    assert Message('pitchwheel', pitch=8191).pitch == 8191
    with pytest.raises(ValueError):
        Message('note_on', channel=16)
    with pytest.raises(ValueError):
        Message('note_on', note=128)
    with pytest.raises(ValueError):
        Message('pitchwheel', pitch=8192)
    with pytest.raises(ValueError):
        Message('pitchwheel', pitch=-8193)
