# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from mido.midifiles.units import bpm2tempo, second2tick, tempo2bpm, tick2second


def test_tempo2bpm():
    # default tempo (500000 ms per quarter note)
    assert tempo2bpm(500000) == 120
    assert tempo2bpm(1000000) == 60
    # x/4 time signature: 4 beats (quarter notes) per bar
    # 60 bpm: 1 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert tempo2bpm(1000000, time_signature=(4, 4)) == 60
    # 120 bpm: 2 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert tempo2bpm(500000, time_signature=(4, 4)) == 120
    assert tempo2bpm(500000, time_signature=(3, 4)) == 120  # 3/4 is the same
    # x/2 time signature: 2 beats (half notes) per bar
    # 60 bpm: 1 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert tempo2bpm(500000, time_signature=(2, 2)) == 60
    # 120 bpm: 2 beat / sec = 4 quarter note / sec: 0.25 sec / quarter note
    assert tempo2bpm(250000, time_signature=(2, 2)) == 120
    assert tempo2bpm(250000, time_signature=(3, 2)) == 120  # 3/2 is the same
    # x/8 time signature: 8 beats (eighth notes) per bar
    # 60 bpm: 1 beat / sec = 0.5 quarter note / sec: 2 sec / quarter note
    assert tempo2bpm(2000000, time_signature=(8, 8)) == 60
    # 120 bpm: 2 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert tempo2bpm(1000000, time_signature=(8, 8)) == 120
    assert tempo2bpm(1000000, time_signature=(8, 8)) == 120  # 6/8 is the same


def test_bpm2tempo():
    # default tempo (500000 ms per quarter note)
    assert bpm2tempo(60) == 1000000
    assert bpm2tempo(120) == 500000
    # x/4 time signature: 4 beats (quarter notes) per bar
    # 60 bpm: 1 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert bpm2tempo(60, time_signature=(4, 4)) == 1000000
    # 120 bpm: 2 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert bpm2tempo(120, time_signature=(4, 4)) == 500000
    assert bpm2tempo(120, time_signature=(3, 4)) == 500000  # 3/4 is the same
    # x/2 time signature: 2 beats (half notes) per bar
    # 60 bpm: 1 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert bpm2tempo(60, time_signature=(2, 2)) == 500000
    # 120 bpm: 2 beat / sec = 4 quarter note / sec: 0.25 sec / quarter note
    assert bpm2tempo(120, time_signature=(2, 2)) == 250000
    assert bpm2tempo(120, time_signature=(3, 2)) == 250000  # 3/2 is the same
    # x/8 time signature: 8 beats (eighth notes) per bar
    # 60 bpm: 1 beat / sec = 0.5 quarter note / sec: 2 sec / quarter note
    assert bpm2tempo(60, time_signature=(8, 8)) == 2000000
    # 120 bpm: 2 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert bpm2tempo(120, time_signature=(8, 8)) == 1000000
    assert bpm2tempo(120, time_signature=(8, 8)) == 1000000  # 6/8 is the same


# TODO: these tests could be improved with better test values such as
# edge cases.
def test_tick2second():
    # default tempo (500000 ms per quarter note)
    assert tick2second(1, ticks_per_beat=100, tempo=500000) == 0.005
    assert tick2second(2, ticks_per_beat=100, tempo=100000) == 0.002


def test_second2tick():
    # default tempo (500000 ms per quarter note)
    assert second2tick(0.001, ticks_per_beat=100, tempo=500000) == 0
    assert second2tick(0.004, ticks_per_beat=100, tempo=500000) == 1
    assert second2tick(0.005, ticks_per_beat=100, tempo=500000) == 1
    assert second2tick(0.0015, ticks_per_beat=100, tempo=100000) == 2
    assert second2tick(0.0025, ticks_per_beat=100, tempo=100000) == 2
