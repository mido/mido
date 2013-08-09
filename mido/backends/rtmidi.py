"""
Experimental wrapper for python-rtmidi:

http://github.com/superquadratic/rtmidi-python
http://pypi.python.org/pypi/python-rtmidi/

This module only supports a limited number of MIDI message types,
as listed below:

    note_off
    note_on
    polytouch
    control_change
    program_change
    aftertouch
    pitchwheel
    songpos
    song_select

This seems to be a limitation in either RtMidi or python-rtmidi.
"""
from __future__ import absolute_import
import os
import time
import mido
import rtmidi
from ..ports import BaseInput, BaseOutput

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
        name = os.environ.get('MIDO_RTMIDI_API')
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
    

def get_devices(api=None):
    devices = []

    api = _get_api_id(api)
    input_names = set(rtmidi.MidiIn(rtapi=api).get_ports())
    output_names = set(rtmidi.MidiOut(rtapi=api).get_ports())

    for name in sorted(input_names | output_names):
        devices.append({
                'name' : name,
                'is_input' : name in input_names,
                'is_output' : name in output_names,
                })

    return devices

def get_api_names():
    return [_api_to_name[n] for n in rtmidi.get_compiled_api()]

class PortCommon(object):
    def _open(self, api=None, virtual=False, callback=None):

        api = _get_api_id(api)
        opening_input = hasattr(self, 'receive')

        if opening_input:
            self._rt = rtmidi.MidiIn(rtapi=api)
            self._rt.ignore_types(False, False, False)
            if callback:
                def callback_wrapper(message_data, data):
                    self._parser.feed(message_data[0])
                    for message in self._parser:
                        callback(message)
                self._rt.set_callback(callback_wrapper)
        else:
            self._rt = rtmidi.MidiOut(rtapi=api)
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

            self._rt.open_port(port_id)

        api = _api_to_name[self._rt.get_current_api()]
        self._device_type = 'RtMidi/{}'.format(api)

    def _close(self):
        self._rt.close_port()

class Input(PortCommon, BaseInput):
    # Todo: sysex messages do not arrive here.
    def _pending(self):
        while 1:
            message = self._rt.get_message()
            if message is None:
                break
            else:
                self._parser.feed(message[0])
            
class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self._rt.send_message(message.bytes())
