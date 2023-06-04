#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Open a MIDI file and print every message in every track.

Support for MIDI files is still experimental.
"""
import sys

from mido import MidiFile

if __name__ == '__main__':
    filename = sys.argv[1]

    midi_file = MidiFile(filename)

    for i, track in enumerate(midi_file.tracks):
        sys.stdout.write(f'=== Track {i}\n')
        for message in track:
            sys.stdout.write(f'  {message!r}\n')
