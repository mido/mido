from __future__ import print_function
from .messages import Message

"""
Searializes MIDI messages to single line text strings.

Module content:

    parse_number(text) => int, float or None
    parse(text) => mido.Message or raise ValueError
    parse_stream(line_generator) => yield mido.Message, error_message
    format(message) => text

Examples of messages:

    note_on channel=0 note=40 velocity=16
    sysex data=(0,14,122,29)

Values can be left out. They will then be set to the default value (0
or ()):

    >>> parse('note_on')
    mido.Message('note_on', channel=0, note=0, velocity=0, time=0)
    >>> parse('sysex')
    mido.Message('sysex', data=(), time=0)

Whitespace around the line is ignored. Sysex data must not contain
whitespace.

If the first word in the line is a number (int or float), it will be
assigned to message.time:

    >>> parse('0.5 note_on channel=1')
    mido.Message('note_on', channel=1, note=0, velocity=0, time=0.5)

"""

def parse_number(text):
    """Parse text as a number.

    Return number or None if text is not a number."""

    for convert in [int, float]:
        try:
            return convert(text)
        except ValueError:
            continue
    else:
        return None

def parse(text):
    """Parse a string of text and return a message.

    The string can span multiple lines, but must contain
    one full message.

    Raises ValueError if the string could not be parsed.
    """
    words = text.split()
    if len(words) < 1:
        raise ValueError('string is empty')

    time = parse_number(words[0])
    if time is not None:
        del words[0]
        if len(words) < 1:
            raise ValueError('no message found after number')

    message = Message(words[0])
    if time:
        message.time = time

    arguments = words[1:]
    valid_arguments = message.spec.args

    names_seen = set()

    for argument in arguments:
        try:
            name, value = argument.split('=')
        except ValueError:
            raise ValueError('missing or extraneous equals sign')

        if name in names_seen:
            raise ValueError('argument passed more than once')
        names_seen.add(name)

        if name == 'data':
            if not value.startswith('(') and value.endswith(')'):
                raise ValueError('missing parentheses in data message')

            try:
                data_bytes = [int(byte) for byte in value[1:-1].split(',')]
            except ValueError:
                raise ValueError('unable to parse data bytes')
            setattr(message, 'data', data_bytes)
        else:
            try:
                setattr(message, name, int(value))
            except AttributeError, exception:
                raise ValueError(exception.message)

    return message


def parse_stream(stream):
    """Parse a stram of messages and yield (message, error_message)

    stream can be any iterable that generates text strings. If
    a line can be parsed, (message, None) is returned. If it can't
    be parsed (None, error_message) is returned. The error message
    containes the line number where the error occured.
    """
    line_number = 1
    for line in stream:
        try:
            line = line.split('#')[0].strip()
            if line:
                yield parse(line), None
        except ValueError, exception:
            error_message = 'line {line_number}: {message}'.format(
                line_number=line_number,
                message=exception.message)
            yield None, error_message            
        line_number += 1


def format(message, include_time=False):
    """Format a message and return as a string."""
    if not isinstance(message, Message):
        raise ValueError('message must be a mido.Message object')

    words = []
    if include_time:
        words.append(str(message.time))
    words.append(message.type)
    for name in message.spec.args:
        value = getattr(message, name)
        if name == 'data':
            value = '({})'.format(','.join([str(byte) for byte in value]))
        words.append('{}={}'.format(name, value))
    
    return ' '.join(words)
