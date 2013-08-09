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
import time
import mido
import rtmidi
from ..ports import BaseInput, BaseOutput

def get_devices():
    devices = []

    input_names = set(rtmidi.MidiIn().get_ports())
    output_names = set(rtmidi.MidiOut().get_ports())

    for name in sorted(input_names | output_names):
        devices.append({
                'name' : name,
                'is_input' : name in input_names,
                'is_output' : name in output_names,
                })

    return devices

class PortCommon(object):
    def _open(self, virtual=False, **kwargs):

        opening_input = hasattr(self, 'receive')

        if opening_input:
            self._rt = rtmidi.MidiIn()
            self._rt.ignore_types(False, False, False)
        else:
            self._rt = rtmidi.MidiOut()
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
