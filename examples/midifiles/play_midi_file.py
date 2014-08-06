#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.

Run with (for example):

    ./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys
import mido
from mido import MidiFile

if len(sys.argv) == 3:
    port_name = sys.argv[2]
else:
    port_name = None

with mido.open_output(port_name) as output:
    try:
        print(output)
        with MidiFile(sys.argv[1]) as midi_file:
            for message in midi_file.play():
                print(message)
                output.send(message)
    except KeyboardInterrupt:
        print()
        output.reset()

