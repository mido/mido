"""
Experimental wrapper for python-rtmidi:
https://pypi.python.org/pypi/python-rtmidi/

Used just like the portmidi ports:

import mido
import mido_rtmidi

with mido_rtmidi.open_output() as port:
    port.send(mido.Messsage('note_on'))


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

import time
import mido
import rtmidi
from mido.ports import BaseInput, BaseOutput, IOPort

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
            
        return self._parser.pending()

class Output(PortCommon, BaseOutput):
    def _send(self, message):
        self.rt.send_message(message.bytes())


def open_input(name=None):
    return Input(name)


def open_output(name=None):
    return Input(name)


def open_input(name=None):
    return IOPort(Input(name), Output(name))


def get_input_names():
    rt = rtmidi.MidiIn()
    return rt.get_ports()


def get_output_names():
    rt = rtmidi.MidiOut()
    return rt.get_ports()


def get_ioport_names():
    return list(set(input_names()) & set(output_names))
