# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Standard MIDI File (SMF) System Exclusive (SysEx) Events

Prefixed with 0xF0: encapsulates SystemExclusiveMessage
Prefixed with 0xF7: encapsulates SystemCommonMessage or SystemRealTimeMessage
"""

from .midi import MidiEvent


class SysExEvent(MidiEvent):

    def __init__(self, delta_time, data):
        # FIXME: this only implements the SystemExclusiveMessage case
        super().__init__(type='sysex', delta_time=delta_time, data=data)
