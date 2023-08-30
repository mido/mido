# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Standard MIDI File (SMF) Events
"""

from mido.protocol.version1.message import BaseMessage


class BaseEvent(BaseMessage):
    """Abstract base class for SMF events."""
    is_meta = False
