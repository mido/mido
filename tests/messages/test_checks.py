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
        check_time(True)


def test_check_time_negative():
    """Ensure negative time value raises ValueError."""
    with raises(ValueError, match="time cannot be negative"):
        check_time(-1)

    with raises(ValueError, match="time cannot be negative"):
        check_time(-0.5)