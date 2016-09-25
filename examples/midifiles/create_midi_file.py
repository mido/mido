#!/usr/bin/env python
"""
Create a new MIDI file with some random notes.

The file is saved to test.mid.
"""

import random
from mido import Message, MidiFile, MidiTrack

notes = [64, 64+7, 64+12]

outfile = MidiFile()

track = MidiTrack()
outfile.tracks.append(track)

track.append(Message('program_change', program=12))

delta = 16
for i in range(4):
    note = random.choice(notes)
    track.append(Message('note_on', note=note, velocity=100, time=delta))
    track.append(Message('note_off', note=note, velocity=100, time=delta))
    
outfile.save('test.mid')

