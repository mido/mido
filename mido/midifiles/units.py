def tick2second(tick: float, ticks_per_beat: int, tempo: int) -> float:
    """Convert absolute time in ticks to seconds.

    Returns absolute time in seconds for a chosen MIDI file time
    resolution (ticks per beat, also called PPQN or pulses per quarter
    note) and tempo (microseconds per beat).
    """
    scale = tempo * 1e-6 / ticks_per_beat
    return tick * scale


def second2tick(second: float, ticks_per_beat: int, tempo: int) -> float:
    """Convert absolute time in seconds to ticks.

    Returns absolute time in ticks for a chosen MIDI file time
    resolution (ticks per beat, also called PPQN or pulses per quarter
    note) and tempo (microseconds per beat).
    """
    scale = tempo * 1e-6 / ticks_per_beat
    return second / scale


def bpm2tempo(bpm: float) -> int:
    """Convert beats per minute to MIDI file tempo.

    Returns microseconds per beat as an integer::

        240 => 250000
        120 => 500000
        60 => 1000000
    """
    # One minute is 60 million microseconds.
    return int(round((60 * 1000000) / bpm))


def tempo2bpm(tempo: int) -> float:
    """Convert MIDI file tempo to BPM.

    Returns BPM as an integer or float::

        250000 => 240
        500000 => 120
        1000000 => 60
    """
    # One minute is 60 million microseconds.
    return (60 * 1000000) / tempo
