# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

import sys
import json
import warnings

import mido


def midifile_to_dict(midi_file):
    tracks = []
    for track in midi_file.tracks:
        tracks.append([vars(msg).copy() for msg in track])

    warnings.warn("ticks_per_beat has been replaced by division",
                  UserWarning)

    return {
        'division': midi_file.division,
        'tracks': tracks,
    }


mid = mido.MidiFile(sys.argv[1])

print(json.dumps(midifile_to_dict(mid), indent=2))
