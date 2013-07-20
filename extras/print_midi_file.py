"""
Open a MIDI file and print every message in every track.

Support for MIDI files is still experimental.
"""
import sys
from mido.midifiles import MidiFile

if __name__ == '__main__':
    filename = sys.argv[1]
    midi_file = MidiFile(filename)
    midi_file._print_tracks()
