#!/bin/bash

function play {
    # mido-play test.mid
    pmidi -p 20:0 -d 0 test.mid
}

./create_midi_file.py && xxd test.mid && play
