#!/usr/bin/env python
"""
Open a MIDI file and print every message in every track.

Support for MIDI files is still experimental.
"""
import sys
from mido import MidiFile

if __name__ == '__main__':
    filename = sys.argv[1]
    with MidiFile(filename) as midi_file:
        for i, track in enumerate(midi_file.tracks):
            sys.stdout.write('=== Track {}\n'.format(i))
            for message in track:
                sys.stdout.write('  {!r}\n'.format(message))
