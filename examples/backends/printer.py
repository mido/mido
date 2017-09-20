"""
A simple custom backend with an output port type which prints messages
to stdout.
"""
from mido.ports import BaseOutput


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
            raise ValueError('unknown port {!r}'.format(self.name))

    def _send(self, message):
        print(message)
