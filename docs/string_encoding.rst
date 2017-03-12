String Encoding
===============

Mido messages can be serialized to a text format, which can be used to
safely store messages in text files, send them across sockets or embed
them in JSON, among other things.

To encode a message, simply call ``str()`` on it::

    >>> cc = control_change(channel=9, control=1, value=122, time=60)
    >>> str(cc)
    'control_change channel=9 control=1 value=122 time=60'

To convert the other way (new method in 1.2)::

    >>> mido.Message.from_str('control_change control=1 value=122')
    <message control_change channel=0 control=1 value=122 time=0>

Alternatively, you can call the ``format_as_string`` function directly:

    >>> mido.format_as_string(cc)
    'control_change channel=9 control=1 value=122 time=60'

If you don't need the time attribute or you want to store it elsewhere, you
can pass ``include_time=False``::

    >>> mido.format_as_string(cc)
    'control_change channel=9 control=1 value=122'

(This option is also available in ``mido.Message.from_str()``.)


Format
------

The format is simple::

    MESSAGE_TYPE [PARAMETER=VALUE ...]

These are the same as the arguments to ``mido.Message()``. The order
of parameters doesn't matter, but each one can only appear once.

Only these character will ever occur in a string encoded Mido message::

    [a-z][0-9][ =_.+()]

or written out::

    'abcdefghijklmnopqrstuvwxyz0123456789 =_.+()'

This means the message can be embedded in most text formats without
any form of escaping.


Parsing
-------

To parse a message, you can use ``mido.parse_string()``::

    >>> parse_string('control_change control=1 value=122 time=0.5')
    <message control_change channel=0 control=1 value=122 time=0.5>

Parameters that are left out are set to their default
values. ``ValueError`` is raised if the message could not be
parsed. Extra whitespace is ignored::

    >>> parse_string('  control_change   control=1  value=122')
    <message control_change channel=0 control=1 value=122 time=0>

To parse messages from a stream, you can use
``mido.messages.parse_string_stream()``::

    for (message, error) in parse_string_stream(open('some_music.text')):
        if error:
            print(error)
        else:
            do_something_with(message)

This will return every valid message in the stream. If a message could
not be parsed, ``message`` will be ``None`` and ``error`` will be an error
message describing what went wrong, as well as the line number where
the error occurred.

The argument to ``parse_string_stream()`` can be any object that
generates strings when iterated over, such as a file or a list.

``parse_string_stream()`` will ignore blank lines and comments (which
start with a # and go to the end of the line). An example of valid
input::

    # A very short song with an embedded sysex message.
    note_on channel=9 note=60 velocity=120 time=0
    # Send some data

    sysex data=(1,2,3) time=0.5

    pitchwheel pitch=4000  # bend the not a little time=0.7
    note_off channel=9 note=60 velocity=60 time=1.0


Examples
--------

And example of messages embedded in JSON::

    {'messages': [
       '0.0 note_on channel=9 note=60 velocity=120',
       '0.5 sysex data=(1,2,3)',
       ...
    ])
