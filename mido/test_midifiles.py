from .midifiles_meta import tempo2bpm, bpm2tempo

def test_tempo2bpm_bpm2tempo():
    for bpm, tempo in [
            (20, 3000000),
            (60, 1000000),
            (120, 500000),
            (240, 250000),
    ]:
        assert bpm == tempo2bpm(tempo)
        assert tempo == bpm2tempo(bpm)
