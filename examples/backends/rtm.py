"""
Experimental backend for rtmidi-python:

http://github.com/superquadratic/rtmidi-python

- Doesn't work with Python 3.3:

  File "rtmidi_python.pyx", line 61, in rtmidi_python.MidiIn.__cinit__
       (rtmidi_  python.cpp:1214)
  TypeError: expected bytes, str found

- Virtual ports don't show up, so other programs can't connect to them.

- There is no way to select API.

Other than that, it works exactly like the included python-rtmidi
backend.
"""
from __future__ import absolute_import
import os
import time
import mido
import rtmidi_python as rtmidi
from mido.ports import BaseInput, BaseOutput

def get_devices():
    devices = []

    input_names = set(rtmidi.MidiIn().ports)
    output_names = set(rtmidi.MidiOut().ports)

    for name in sorted(input_names | output_names):
        devices.append({
                'name' : name,
                'is_input' : name in input_names,
                'is_output' : name in output_names,
                })

    return devices

class PortCommon(object):
    def _open(self, virtual=False, callback=None):
        opening_input = hasattr(self, 'receive')

        if opening_input:
            self._rt = rtmidi.MidiIn()
            self._rt.ignore_types(False, False, False)
            if callback:
                def callback_wrapper(message, delta_time):
                    self._parser.feed(message)
                    for message in self._parser:
                        callback(message)
                self._rt.callback = self._callback = callback_wrapper
                self._has_callback = True
            else:
                self._has_callback = False
        else:
            self._rt = rtmidi.MidiOut()
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

            self._rt.open_port(port_id)

        self._device_type = 'rtmidi_python'

    def _close(self):
        self._rt.close_port()

class Input(PortCommon, BaseInput):
    # Todo: sysex messages do not arrive here.
    def _receive(self, block=True):
        if self._has_callback:
            raise IOError('a callback is currently set for this port')

        while True:
            (message, delta_time) = self._rt.get_message()
            if message is None:
                break
            else:
                self._parser.feed(message)
            
class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self._rt.send_message(message.bytes())
