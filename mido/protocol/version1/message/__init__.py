# SPDX-FileCopyrightText: 2016 Ole Martin Bjorndalen <ombdalen@gmail.com>
# SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
MIDI 1.0 Protocol Messages
"""

from .checks import check_time
from .specs import (SPEC_LOOKUP, SPEC_BY_TYPE, SPEC_BY_STATUS,
                    MIN_PITCHWHEEL, MAX_PITCHWHEEL, MIN_SONGPOS, MAX_SONGPOS)
from .message import (BaseMessage, Message, parse_string,
                      format_as_string, parse_string_stream)

__all__ = [
    'Message',
]
