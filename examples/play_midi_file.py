#!/usr/bin/env python
"""                                                                            
Play MIDI file on output port.

Run with (for example):

    ./play_midi_file.py 'SH-201 MIDI 1' 'test.mid'
"""

import sys
import mido
from mido.midifiles import MidiFile

with mido.open_output(sys.argv[1]) as output:
    try:
        print(output)
        with MidiFile(sys.argv[2]) as midi_file:
            for message in midi_file.play():
                print(message)
                output.send(message)
    except KeyboardInterrupt:
        print()
