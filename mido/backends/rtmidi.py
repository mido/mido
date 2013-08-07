"""
Experimental wrapper for python-rtmidi:
https://pypi.python.org/pypi/python-rtmidi/

This module only supports a limited number of MIDI message types,
as listed below. (I am not sure where this limitation arises.)

rtmidi => rtmidi
-----------------
note_off channel=0 note=0 velocity=0 time=0
note_on channel=0 note=0 velocity=0 time=0
polytouch channel=0 note=0 value=0 time=0
control_change channel=0 control=0 value=0 time=0
program_change channel=0 program=0 time=0
aftertouch channel=0 value=0 time=0
pitchwheel channel=0 pitch=0 time=0
songpos pos=0 time=0
song_select song=0 time=0

rtmidi => portmidi
-------------------
Received note_off channel=0 note=0 velocity=0 time=0
Received note_on channel=0 note=0 velocity=0 time=0
Received polytouch channel=0 note=0 value=0 time=0
Received control_change channel=0 control=0 value=0 time=0
Received program_change channel=0 program=0 time=0
Received aftertouch channel=0 value=0 time=0
Received pitchwheel channel=0 pitch=0 time=0
Received sysex data=() time=0    !
Received songpos pos=0 time=0
Received song_select song=0 time=0

portmidi => rtmidi
-------------------

note_off channel=0 note=0 velocity=0 time=0
note_on channel=0 note=0 velocity=0 time=0
polytouch channel=0 note=0 value=0 time=0
control_change channel=0 control=0 value=0 time=0
program_change channel=0 program=0 time=0
aftertouch channel=0 value=0 time=0
pitchwheel channel=0 pitch=0 time=0
songpos pos=0 time=0
song_select song=0 time=0
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

def get_output_names():
    rt = rtmidi.MidiOut()
    return rt.get_ports()


class PortCommon(object):
    def _open(self, **kwargs):
        opening_input = isinstance(self, Input)

        if opening_input:
            self.rt = rtmidi.MidiIn()
        else:
            self.rt = rtmidi.MidiOut()

        available_ports = self.rt.get_ports()
        if self.name is None:
            # Todo: this could fail if list is empty.
            # Also, it assumes that the first port is the default port.
            self.name = available_ports[0]
            port_id = 0
        else:
            # Todo: this could fail if the name is not in the list.
            port_id = available_ports.index(self.name)

        self.rt.open_port(port_id)

    def _close(self):
        del self.rt

    def _get_device_type(self):
        return 'RtMidi'


class Input(PortCommon, BaseInput):
    # Todo: sysex messages do not arrive here.
    def _pending(self):
        while 1:
            message = self.rt.get_message()
            if message is None:
                break
            else:
                self._parser.feed(message[0])
            
class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self.rt.send_message(message.bytes())
