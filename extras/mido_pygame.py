"""
Mido ports for pygame.midi.

Pygame uses PortMidi, so this is perhaps not very useful.

http://www.pygame.org/docs/ref/midi.html
"""

import atexit
from pygame import midi
from mido.ports import BaseInput, BaseOutput, IOPort

def get_device(device_id):
    midi.init()
    
    keys = ['interface', 'name', 'is_input', 'is_output', 'opened']
    info = dict(zip(keys, midi.get_device_info(device_id)))
    info['device_id'] = device_id
    return info

def get_devices():
    midi.init()

    return [get_device() for device_id in range(midi.get_count())]


def get_input_names():
    names = [dev['name'] for dev in get_devices() if dev['is_input']]
    return list(sorted(names))


def get_output_names():
    names = [dev['name'] for dev in get_devices() if dev['is_output']]
    return list(sorted(names))


def get_ioport_names():
    names = set(get_input_names()) & set(get_output_names())
    return list(sorted(names))


def open_input(name=None):
    return Input(name)


def open_output(name=None):
    return Output(name)


def open_ioport(name=None):
    return IOPort(Input(name), Output(name))

class PortCommon(object):
    """
    Mixin with common things for input and output ports.
    """
    def _open(self):
        midi.init()

        self.device = None

        opening_input = (self.__class__ is Input)

        if self.name is None:
            self.device = self._get_default_device(opening_input)
            self.name = self.device['name']
        else:
            self.device = self._get_named_device(self.name, opening_input)

        if self.device['opened']:
            if opening_input:
                devtype = 'input'
            else:
                devtype = 'output'
            raise IOError('{} port {!r} is already open'.format(devtype,
                                                                self.name))

        if opening_input:
            self._port = midi.Input(self.device['device_id'])
        else:
            self._port = midi.Output(self.device['device_id'])

        atexit.register(self.close)

    def _get_device_type(self):
        return self.device['interface']

    def _get_default_device(self, get_input):
        if get_input:
            device_id = midi.get_default_input_id()
        else:
            device_id = midi.get_default_output_id()

        if device_id < 0:
            raise IOError('no default port found')

        return get_device(device_id)

    def _get_named_device(self, name, get_input):
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
        
        return self._parser.pending()


class Output(PortCommon, BaseOutput):
    """
    PortMidi output port
    """

    def _send(self, message):
        print(message)
        if message.type == 'sysex':
            self._port.write_sys_ex(midi.time(), message.bytes())
        else:
            self._port.write_short(*message.bytes())
