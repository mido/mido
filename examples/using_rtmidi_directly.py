"""
First example from here modified to use Mido messages:

    http://pypi.python.org/pypi/python-rtmidi/
"""
import time
import mido
import rtmidi

midiout = rtmidi.MidiOut()
available_ports = midiout.get_ports()

if available_ports:
    midiout.open_port(0)
else:
    midiout.open_virtual_port("My virtual output")

# Original example:
# note_on = [0x99, 60, 112] # channel 10, middle C, velocity 112
# note_off = [0x89, 60, 0]

note_on = mido.Message('note_on', channel=9, note=60, velocity=112).bytes()
note_off = mido.Message('note_off', channel=9, note=60, velocity=0).bytes()
midiout.send_message(note_on)
time.sleep(0.5)
midiout.send_message(note_off)

del midiout
