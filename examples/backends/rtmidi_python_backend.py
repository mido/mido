"""Backend for rtmidi-python:

https://pypi.python.org/pypi/rtmidi-python

To use this backend copy (or link) it to somewhere in your Python path
and call:

    mido.set_backend('rtmidi_python_backend')

or set shell variable $MIDO_BACKEND to rtmidi_python_backend:

Todo:

* add support for APIs.

* active_sensing is still filtered. (The same is true for
  mido.backends.rtmidi.)There may be a way to remove this filtering.

"""
from __future__ import absolute_import
import os
import time
from Queue import Queue
import rtmidi_python as rtmidi
# Todo: change this to a relative import if the backend is included in
# the package.
from mido.ports import BaseInput, BaseOutput

def get_devices(api=None, **kwargs):
    devices = []

    input_names = set(rtmidi.MidiIn().ports)
    output_names = set(rtmidi.MidiOut().ports)

    for name in sorted(input_names | output_names):
        devices.append({
                'name': name,
                'is_input': name in input_names,
                'is_output': name in output_names,
                })

    return devices

class PortCommon(object):
    def _open(self, api=None, virtual=False, **kwargs):

        self._queue = Queue()

        # rtapi = _get_api_id(api)
        opening_input = hasattr(self, 'receive')
        
        if opening_input:
            self._rt = rtmidi.MidiIn(api)
            self._rt.ignore_types(False, False, True)
            self.callback = kwargs.get('callback')
        else:
            self._rt = rtmidi.MidiOut()  # rtapi=rtapi)
            # Turn of ignore of sysex, time and active_sensing.

        ports = self._rt.ports

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

        # api = _api_to_name[self._rt.get_current_api()]
        api = ''
        self._device_type = 'RtMidi/{}'.format(api)
        if virtual:
            self._device_type = 'virtual {}'.format(self._device_type)

    @property
    def callback(self):
        return self._rt._callback

    @callback.setter
    def callback(self, func):
        self._rt.callback = func

    def _callback_wrapper(self, *args, **kw):
        asodosaid

        self._parser.feed(message_data[0])
        for message in self._parser:
            if self.callback:
                self.callback(message)

    def _close(self):
        self._rt.close_port()
        del self._rt  # Virtual ports are closed when this is deleted.

class Input(PortCommon, BaseInput):
    def _receive(self, block=True):
        # Since there is no blocking read in RtMidi, the block
        # flag is ignored and the enclosing receive() takes care
        # of blocking.

        while True:
            message_data, timestamp = self._rt.get_message()
            if message_data is None:
                break
            else:
                self._parser.feed(message_data)

class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self._rt.send_message(message.bytes())
