"""
Backend for python-rtmidi:

http://pypi.python.org/pypi/python-rtmidi/
"""
from __future__ import absolute_import
import os
import time
import rtmidi
from ..ports import BaseInput, BaseOutput
from ..parser import parse

def _get_api_lookup():
    api_to_name = {}
    name_to_api = {}

    for name in dir(rtmidi):
        if name.startswith('API_'):
            value = getattr(rtmidi, name)
            name = name.replace('API_', '')
            name_to_api[name] = value
            api_to_name[value] = name

    return api_to_name, name_to_api

_api_to_name, _name_to_api = _get_api_lookup()

def _get_api_id(name=None):
    if name is None:
        return rtmidi.API_UNSPECIFIED

    try:
        api = _name_to_api[name]
    except KeyError:
        raise ValueError('unknown API {}'.format(name))    

    if name in get_api_names():
        return api
    else:
        raise ValueError('API {} not compiled in'.format(name))
    

def get_devices(api=None, **kwargs):
    devices = []

    rtapi = _get_api_id(api)
    input_names = set(rtmidi.MidiIn(rtapi=rtapi).get_ports())
    output_names = set(rtmidi.MidiOut(rtapi=rtapi).get_ports())

    for name in sorted(input_names | output_names):
        devices.append({
                'name': name,
                'is_input': name in input_names,
                'is_output': name in output_names,
                })

    return devices

def get_api_names():
    return [_api_to_name[n] for n in rtmidi.get_compiled_api()]

class PortCommon(object):
    def _open(self, api=None, virtual=False, **kwargs):

        rtapi = _get_api_id(api)
        opening_input = hasattr(self, 'receive')
        
        if opening_input:
            self._rt = rtmidi.MidiIn(rtapi=rtapi)
            self._rt.ignore_types(False, False, True)
            if self.callback:
                def callback_wrapper(message_data, data):
                    message = parse(message_data[0])
                    if message and self.callback:
                        self.callback(message)
                self._rt.set_callback(callback_wrapper)
        else:
            self._rt = rtmidi.MidiOut(rtapi=rtapi)
            # Turn of ignore of sysex, time and active_sensing.

        ports = self._rt.get_ports()

        if virtual:
            if self.name is None:
                raise IOError('virtual port must have a name')
            self._rt.open_virtual_port(self.name)
        else:
            if self.name is None:
                # Todo: this could fail if list is empty.
                # In RtMidi, the default port is the first port.
                try:
                    self.name = ports[0]
                except IndexError:
                    raise IOError('no ports available')

            try:
                port_id = ports.index(self.name)
            except ValueError:
                raise IOError('unknown port {!r}'.format(self.name))

            try:
                self._rt.open_port(port_id)
            except RuntimeError as err:
                raise IOError(*err.args)

        api = _api_to_name[self._rt.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(api)
        if virtual:
            self._device_type = 'virtual {}'.format(self._device_type)

    def _close(self):
        self._rt.close_port()
        del self._rt  # Virtual ports are closed when this is deleted.

class Input(PortCommon, BaseInput):
    def _receive(self, block=True):
        # Since there is no blocking read in RtMidi, the block
        # flag is ignored and the enclosing receive() takes care
        # of blocking.

        while 1:
            message_data = self._rt.get_message()
            if message_data is None:
                break
            else:
                message = parse(message_data[0])
                if message:
                    self._messages.append(message)
 
class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self._rt.send_message(message.bytes())
