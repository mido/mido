"""
Mido ports for pygame.midi.

Pygame uses PortMidi, so this is perhaps not very useful.

http://www.pygame.org/docs/ref/midi.html
"""

from __future__ import absolute_import
from pygame import midi
from ..ports import BaseInput, BaseOutput

def _get_device(device_id):
    midi.init()    

    keys = ['interface', 'name', 'is_input', 'is_output', 'opened']
    info = dict(zip(keys, midi.get_device_info(device_id)))
    info['id'] = device_id
    info['name'] = info['name'].decode('utf-8') # Todo: correct encoding?
    return info

def _get_default_device(get_input):
    if get_input:
        device_id = midi.get_default_input_id()
    else:
        device_id = midi.get_default_output_id()

    if device_id < 0:
        raise IOError('no default port found')

    return _get_device(device_id)

def _get_named_device(name, get_input):
    # Look for the device by name and type (input / output)
    for device in get_devices():
        if device['name'] != name:
            continue

        # Skip if device is the wrong type
        if get_input:
            if device['is_output']:
                continue
        else:
            if device['is_input']:
                continue

        if device['opened']:
            raise IOError('port already opened: {!r}'.format(name))

        return device
    else:
        raise IOError('unknown port: {!r}'.format(name))


def get_devices():
    midi.init()

    return [_get_device(device_id) for device_id in range(midi.get_count())]


class PortCommon(object):
    """
    Mixin with common things for input and output ports.
    """
    def _open(self, **kwargs):
        midi.init()

        opening_input = hasattr(self, 'receive')

        if self.name is None:
            self.device = _get_default_device(opening_input)
            self.name = self.device['name']
        else:
            self.device = _get_named_device(self.name, opening_input)

        if self.device['opened']:
            if opening_input:
                devtype = 'input'
            else:
                devtype = 'output'
            raise IOError('{} port {!r} is already open'.format(devtype,
                                                                self.name))
        if opening_input:
            self._port = midi.Input(self.device['id'])
        else:
            self._port = midi.Output(self.device['id'])

        self._device_type = 'pygame'

    def _close(self):
        self._port = None  # Todo: this should call self._port.close()

class Input(PortCommon, BaseInput):
    """
    PortMidi Input port
    """

    def _pending(self):
        # I get hanging notes if MAX_EVENTS > 1, so I'll have to
        # resort to calling Pm_Read() in a loop until there are no
        # more pending events.

        while self._port.poll():
            event = self._port.read(1)[0]
            midi_bytes = event[0]
            self._parser.feed(midi_bytes)
            print(self._messages)


class Output(PortCommon, BaseOutput):
    """
    PortMidi output port
    """

    def _send(self, message):
        if message.type == 'sysex':
            self._port.write_sys_ex(midi.time(), message.bytes())
        elif message.type == 'sysex_end':
            # This crashes PortMidi, so it's best to ignore it.
            pass
        else:
            self._port.write_short(*message.bytes())
