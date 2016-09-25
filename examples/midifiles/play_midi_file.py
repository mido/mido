#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.

Run with (for example):

    ./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys
import mido
from mido import MidiFile

filename = sys.argv[1]
if len(sys.argv) == 3:
    portname = sys.argv[2]
else:
    portname = None

with mido.open_output(portname) as output:
    try:
        for message in MidiFile(filename).play():
            print(message)
            output.send(message)

    except KeyboardInterrupt:
        print()
        output.reset()
