#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Create a new MIDI file with some random notes.

The file is saved to test.mid.
"""
import random
import sys

from mido import MAX_PITCHWHEEL, MidiEvent, MidiFile, MidiTrack

notes = [64, 64 + 7, 64 + 12]

outfile = MidiFile()

track = MidiTrack()
outfile.tracks.append(track)

track.append(MidiEvent(type='program_change', program=12))

delta_time = 300
ticks_per_expr = int(sys.argv[1]) if len(sys.argv) > 1 else 20
for i in range(4):
    note = random.choice(notes)
    track.append(MidiEvent(delta_time=delta_time,
                           type='note_on', note=note, velocity=100))
    for j in range(delta_time // ticks_per_expr):
        pitch = MAX_PITCHWHEEL * j * ticks_per_expr // delta_time
        track.append(MidiEvent(delta_time=ticks_per_expr,
                               type='pitchwheel', pitch=pitch, ))
    track.append(MidiEvent(delta_time=0,
                           type='note_off', note=note, velocity=100))

outfile.save('test.mid')
