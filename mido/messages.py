"""
Most of this has been moved into the mido.msg package.

The rest of Mido still references this file so we have to import
some stuff into here for now.
"""

from .msg.msg import BaseMessage, Message

# Todo: these are used by the old tests. Removed them
# when the tests have been removed/rewritten.
from .msg.defs import MIN_PITCHWHEEL, MAX_PITCHWHEEL


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


from .msg.check import check_time


def parse_string(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    return Message.from_str(text)


def parse_string_stream(stream):
    """Parse a stram of messages and yield (message, error_message)

    stream can be any iterable that generates text strings, where each
    string is a string encoded message.

    If a string can be parsed, (message, None) is returned. If it
    can't be parsed (None, error_message) is returned. The error
    message containes the line number where the error occurred.
    """
    line_number = 1
    for line in stream:
        try:
            line = line.split('#')[0].strip()
            if line:
                yield parse_string(line), None
        except ValueError as exception:
            error_message = 'line {line_number}: {message}'.format(
                line_number=line_number,
                message=exception.args[0])
            yield None, error_message
        line_number += 1


def format_as_string(message, include_time=True):
    """Format a message and return as a string.

    This is equivalent to str(message).

    To leave out the time attribute, pass include_time=False.
    """
    return message.to_str(include_time=include_time)
