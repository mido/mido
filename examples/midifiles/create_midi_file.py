#!/usr/bin/env python
"""
Create a new MIDI file with some random notes.

The file is saved to test.mid.
"""

import random
from mido import Message
from mido.midifiles import MidiFile, MidiTrack

notes = [64, 64+7, 64+12]

with MidiFile() as f:
    track = MidiTrack()
    f.tracks.append(track)

    track.append(Message('program_change', program=12))

    delta = 16
    for i in range(4):
        note = random.choice(notes)
        track.append(Message('note_on', note=note, velocity=100, time=delta))
        track.append(Message('note_off', note=note, velocity=100, time=delta))

    f.save('test.mid')
