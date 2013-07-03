String Encoding
================

Mido messages can be serialized to a text format, which can be used to
safely store messages in text files, send them across sockets or embed
them in JSON, among other things.

To encode a message, simply call `str()` on it:

.. code:: python

    >>> n = control_change(channel=9, control=1, value=122, time=60)
    >>> str(n)
    '60 control_change channel=9 control=1 value=122'


Format
-------

The format is simple::

    [TIME] MESSAGE_TYPE [PARAMETER=VALUE ...]

`str()` will always generate a time, but the parser accepts lines
without a time, in which case `time` will be set to 0. The formatter (`str()`)
will add a time in front of the messages if `time` is != 0.

Only these character will ever occur in a string encoded Mido message::

    [a-z][0-9][ =_.+()]

or written out::

    'abcdefghijklmnopqrstuvwxyz0123456789 =_.+()'

This means the message can be embedded in most text formats without
any form of escaping.


Parsing
--------

To parse a message, you can use `mido.messages.parse_string()`:

.. code:: python

    >>> parse_string('  control_change   control=1  value=122')
    <control_change message channel=0, control=1, value=122, time=0>

If the first word in the string is a number, the message's `time` will
be set to this value:

.. code:: python

    >>> parse_string('0.5 control_change control=1 value=122')
    <control_change message channel=0, control=1, value=122, time=0.5>

Parameters that are left out are set to their default
values. `ValueError` is raised if the message could not be
parsed. Extra whitespace is ignored.

To parse messages from a stream, you can use
`mido.messages.parse_string_stream()`.

.. code:: python

    for (message, error) in parse_string_stream(open('some_music.text')):
        if error:
            print(error)
        else:
            do_something_with(message)

This will return every valid message in the stream. If a message could
not be parsed, `message` will be `None` and `error` will be an error
message describing what went wrong, as well as the line number where
the error occured.

The argument to `parse_string_stream` can be any object that generates
strings when iterated over, such as a file or a list.

`parse_string_stream` will ignore blank lines and comments (which
start with a # and go to the end of the line). An example of valid input::

    # A very short song with an embedded sysex message.
    0.0 note_on channel=9 note=60 velocity=120
    # Send some data

    0.5 sysex data=(1,2,3)

    0.7 pitchwheel pitch=4000  # bend the not a little
    1.0 note_off channel=9 note=60 velocity=60


Examples
---------

And example of messages embedded in JSON::

    {'messages': [
       '0.0 note_on channel=9 note=60 velocity=120',
       '0.5 sysex data=(1,2,3)',
       ...
    ])
