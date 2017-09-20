import sys
import json
import mido


def midifile_to_dict(mid):
    tracks = []
    for track in mid.tracks:
        tracks.append([vars(msg).copy() for msg in track])

    return {
        'ticks_per_beat': mid.ticks_per_beat,
        'tracks': tracks,
    }


mid = mido.MidiFile(sys.argv[1])

print(json.dumps(midifile_to_dict(mid), indent=2))
