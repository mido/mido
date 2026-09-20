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


def test_amidi_backend_uses_base_ports():
    # The amidi backend was left importing mixins that had been replaced by the
    # base port classes, so importing it raised ModuleNotFoundError. (#313)
    from mido.backends import amidi
    from mido.ports import BaseInput, BaseOutput

    assert issubclass(amidi.Input, BaseInput)
    assert issubclass(amidi.Output, BaseOutput)
    assert amidi.Input.is_input
    assert amidi.Output.is_output
    assert amidi.get_devices
