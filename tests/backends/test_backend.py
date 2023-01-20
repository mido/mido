# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from mido.backends.backend import Backend


def test_split_api():
    backend = Backend('test')
    assert backend.name == 'test'
    assert backend.api is None

    backend = Backend('test/ALSA')
    assert backend.name == 'test'
    assert backend.api == 'ALSA'
