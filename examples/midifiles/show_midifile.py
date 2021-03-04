#!/usr/bin/env python
import sys
import argparse
import mido


def parse_args():
    parser = argparse.ArgumentParser()
    arg = parser.add_argument

    arg('midifile', nargs=1)

    return parser.parse_args()


args = parse_args()
print(repr(mido.MidiFile(args.midifile[0])))
