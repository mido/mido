DEFAULT_TEMPO = 500000  # microseconds per quarter note (i.e. 120 bpm in 4/4)
DEFAULT_TICKS_PER_BEAT = 480  # ticks per quarter note
DEFAULT_TIME_SIGNATURE = (4, 4)


def tick2second(tick, ticks_per_beat, tempo):
    """Convert absolute time in ticks to seconds.

    Returns absolute time in seconds for a chosen MIDI file time resolution
    (ticks/pulses per quarter note, also called PPQN) and tempo (microseconds
    per quarter note).
    """
    scale = tempo * 1e-6 / ticks_per_beat
    return tick * scale


def second2tick(second, ticks_per_beat, tempo):
    """Convert absolute time in seconds to ticks.

    Returns absolute time in ticks for a chosen MIDI file time resolution
    (ticks/pulses per quarter note, also called PPQN) and tempo (microseconds
    per quarter note). Normal rounding applies.
    """
    scale = tempo * 1e-6 / ticks_per_beat
    return int(round(second / scale))


def bpm2tempo(bpm, time_signature=(4, 4)):
    """Convert BPM (beats per minute) to MIDI file tempo (microseconds per
    quarter note).

    Depending on the chosen time signature a bar contains a different number of
    beats. These beats are multiples/fractions of a quarter note, thus the
    returned BPM depend on the time signature. Normal rounding applies.
    """
    return int(round(60 * 1e6 / bpm * time_signature[1] / 4.))


def tempo2bpm(tempo, time_signature=(4, 4)):
    """Convert MIDI file tempo (microseconds per quarter note) to BPM (beats
    per minute).

    Depending on the chosen time signature a bar contains a different number of
    beats. These beats are multiples/fractions of a quarter note, thus the
    returned tempo depends on the time signature.
    """
    return 60 * 1e6 / tempo * time_signature[1] / 4.


def tick2beat(tick, ticks_per_beat, time_signature=(4, 4)):
    """Convert ticks to beats.

    Returns beats for a chosen MIDI file time resolution (ticks/pulses per
    quarter note, also called PPQN) and time signature.
    """
    return tick / (4. * ticks_per_beat / time_signature[1])


def beat2tick(beat, ticks_per_beat, time_signature=(4, 4)):
    """Convert beats to ticks.

    Returns ticks for a chosen MIDI file time resolution (ticks/pulses per
    quarter note, also called PPQN) and time signature. Normal rounding
    applies.
    """
    return int(round(beat * 4. * ticks_per_beat / time_signature[1]))
