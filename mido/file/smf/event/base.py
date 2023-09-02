#  SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Standard MIDI File (SMF) Events Base
"""

from mido.protocol.version1.message.base import BaseMessage


class MtrkEvent(BaseMessage):
    """Abstract base class for SMF events."""
    is_meta = False
    delta_time: int
