from mido.midifiles.units import *


def test_tempo2bpm():
    # default tempo (500000 ms per quarter note)
    assert tempo2bpm(500000) == 120
    assert tempo2bpm(1000000) == 60
    # x/4 time signature: 4 beats (quarter notes) per bar
    # 60 bpm: 1 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert bpm2tempo(1000000, time_signature=(4, 4)) == 60
    # 120 bpm: 2 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert bpm2tempo(500000, time_signature=(4, 4)) == 120
    assert bpm2tempo(500000, time_signature=(3, 4)) == 120  # 3/4 is the same
    # x/2 time signature: 2 beats (half notes) per bar
    # 60 bpm: 1 beat / sec = 2 quarter note / sec: 0.5 sec / quarter note
    assert bpm2tempo(500000, time_signature=(2, 2)) == 60
    # 120 bpm: 2 beat / sec = 4 quarter note / sec: 0.25 sec / quarter note
    assert bpm2tempo(250000, time_signature=(2, 2)) == 120
    assert bpm2tempo(250000, time_signature=(3, 2)) == 120  # 3/2 is the same
    # x/8 time signature: 8 beats (eighth notes) per bar
    # 60 bpm: 1 beat / sec = 0.5 quarter note / sec: 2 sec / quarter note
    assert bpm2tempo(2000000, time_signature=(8, 8)) == 60
    # 120 bpm: 2 beat / sec = 1 quarter note / sec: 1 sec / quarter note
    assert bpm2tempo(1000000, time_signature=(8, 8)) == 120
    assert bpm2tempo(1000000, time_signature=(8, 8)) == 120  # 6/8 is the same


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
    # TODO: Python 2 and 3 rounds differently, find a solution?
    #       The result produced by Python 3 seems the way to go
    assert second2tick(0.0015, ticks_per_beat=100, tempo=100000) == 2
    assert second2tick(0.0025, ticks_per_beat=100, tempo=100000) == 2


def test_tick2beat():
    # default 4/4 time signature
    assert tick2beat(100, ticks_per_beat=100) == 1
    assert tick2beat(200, ticks_per_beat=100) == 2
    # default tempo and ticks (480 per quarter note)
    assert tick2beat(480, ticks_per_beat=480) == 1
    # 2/4 time signature
    assert tick2beat(480, ticks_per_beat=480, time_signature=(2, 4)) == 1
    # 2/2 time signature: 960 ticks per beat (half note = 2 quarter notes)
    assert tick2beat(960, ticks_per_beat=480, time_signature=(2, 2)) == 1
    # 3/8 time signature: 240 ticks per beat (eighth note = 0.5 quarter note)
    assert tick2beat(240, ticks_per_beat=480, time_signature=(3, 8)) == 1


def test_beat2tick():
    # default 4/4 time signature
    assert beat2tick(1, ticks_per_beat=100) == 100
    assert beat2tick(1.5, ticks_per_beat=100) == 150
    assert beat2tick(0.01, ticks_per_beat=100) == 1
    # division rounds to the closest even integer
    assert beat2tick(0.004, ticks_per_beat=100) == 0
    assert beat2tick(0.005, ticks_per_beat=100) == 1
    # TODO: Python 2 and 3 rounds differently, find a solution?
    #       The result produced by Python 3 seems the way to go
    assert beat2tick(0.015, ticks_per_beat=100) == 2
    assert beat2tick(0.025, ticks_per_beat=100) == 2
    # x/4 time signature: beat = quarter note: 480 ticks / beat
    assert beat2tick(1, ticks_per_beat=480) == 480
    assert beat2tick(1, ticks_per_beat=480, time_signature=(3, 4)) == 480
    assert beat2tick(1, ticks_per_beat=300, time_signature=(3, 4)) == 300
    # x/2 time signature: beat = half note (2 quarter notes): 960 ticks / beat
    assert beat2tick(1, ticks_per_beat=480, time_signature=(2, 2)) == 960
    assert beat2tick(1, ticks_per_beat=480, time_signature=(3, 2)) == 960
    assert beat2tick(1, ticks_per_beat=300, time_signature=(3, 2)) == 600
    # x/8 time signature: beat = eighth note (0.5 quarter n.): 240 ticks / beat
    assert beat2tick(1, ticks_per_beat=480, time_signature=(8, 8)) == 240
    assert beat2tick(1, ticks_per_beat=480, time_signature=(6, 8)) == 240
    assert beat2tick(1, ticks_per_beat=300, time_signature=(6, 8)) == 150
