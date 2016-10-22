"""
Most of this has been moved into the mido.msg package.

The rest of Mido still references this file so we have to import
some stuff into here for now.
"""

from .messages import BaseMessage, Message
from .messages import parse_string, format_as_string, parse_string_stream

# Todo: these are used by the old tests. Removed them
# when the tests have been removed/rewritten.
from .defs import MIN_PITCHWHEEL, MAX_PITCHWHEEL


# This is used by MidiFile. This should be changed.
def build_message(spec, bytes, time=0):
    """Build message from bytes.

    This is used by Parser and MidiFile. bytes is a full list
    of bytes for the message including the status byte. For sysex
    messages, the end byte is not included. Examples:

        build_message(spec, [0x80, 20, 100])
        build_message(spec, [0xf0, 1, 2, 3])

    No type or value checking is done, so you need to do that before
    you call this function. (This includes time.) 0xf7 is not allowed
    as status byte.
    """
    raise NotImplemented()


def get_spec():
    raise NotImplemented()


from .check import check_time
