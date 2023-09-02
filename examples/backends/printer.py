# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
A simple custom backend with an output port type which prints messages
to stdout.
"""

from mido.port.ports import BaseOutput


def get_devices():
    return [{'name': 'The Print Port',
             'is_input': False,
             'is_output': True}]


class Output(BaseOutput):
    def _open(self, **kwargs):
        device = get_devices()[0]

        if self.name is None:
            self.name = device['name']
        elif self.name != device['name']:
            raise ValueError(f'unknown port {self.name!r}')

    def _send(self, message):
        print(message)
