# SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
#
# SPDX-License-Identifier: MIT

from fractions import Fraction


def tick2second(tick, ticks_per_beat, tempo):
    """Converts time in MIDI ticks to seconds.

    .. deprecated:: 2.0.0

       Please use :func:`ticks2seconds` instead
    """
    return ticks2seconds(tick, ticks_per_beat, tempo)


def ticks2seconds(ticks_time, resolution, tempo):
    """Converts time in MIDI ticks to seconds.

    Returns fractional time in seconds for a chosen MIDI file time resolution
    (ticks/pulses per quarter note, also called PPQN) and tempo (microseconds
    per quarter note).
    """
    scale = Fraction(tempo, resolution) * Fraction(1e-6)
    return ticks_time * scale


def second2tick(second, ticks_per_beat, tempo):
    """Converts time in seconds to MIDI ticks.

    .. deprecated:: 2.0.0

       Please use :func:`seconds2ticks` instead
    """
    return seconds2ticks(second, ticks_per_beat, tempo)


def seconds2ticks(seconds_time, resolution, tempo):
    """Converts time in seconds to MIDI ticks.

    Returns time in ticks for a chosen MIDI file time resolution
    (ticks/pulses per quarter note, also called PPQN) and tempo (microseconds
    per quarter note). Normal rounding applies.
    """
    scale = Fraction(tempo, resolution) * Fraction(1e-6)
    return round(seconds_time / scale, ndigits=None)


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
    beats. The beats are multiples/fractions of a quarter note, thus the
    returned tempo depends on the time signature denominator.
    """
    return 60 * 1e6 / tempo * time_signature[1] / 4.
