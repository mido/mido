#!/bin/bash

# SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

function play {
    # mido-play test.mid
    pmidi -p 20:0 -d 0 test.mid
}

./create_midi_file.py && xxd test.mid && play
