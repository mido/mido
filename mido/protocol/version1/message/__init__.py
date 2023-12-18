# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDI 1.0 Protocol Messages
"""

__all__ = [
    'Message',
]

from .checks import check_time
from .message import (
    BaseMessage,
    Message,
    format_as_string,
    parse_string,
    parse_string_stream,
)
from .specs import (
    MAX_PITCHWHEEL,
    MAX_SONGPOS,
    MIN_PITCHWHEEL,
    MIN_SONGPOS,
    SPEC_BY_STATUS,
    SPEC_BY_TYPE,
    SPEC_LOOKUP,
)
