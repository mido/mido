from mido.midifiles.units import tempo2bpm, bpm2tempo, tick2second, second2tick


def test_tempo2bpm_bpm2tempo():
    for bpm, tempo in [
            (20, 3000000),
            (60, 1000000),
            (120, 500000),
            (240, 250000),
    ]:
        assert bpm == tempo2bpm(tempo)
        assert tempo == bpm2tempo(bpm)


# TODO: these tests could be improved with better test values such as
# edge cases.

def test_tick2second():
    assert tick2second(1, ticks_per_beat=100, tempo=500000) == 0.005
    assert tick2second(2, ticks_per_beat=100, tempo=100000) == 0.002


def test_second2tick():
    assert second2tick(0.005, ticks_per_beat=100, tempo=500000) == 1
    assert second2tick(0.002, ticks_per_beat=100, tempo=100000) == 2
