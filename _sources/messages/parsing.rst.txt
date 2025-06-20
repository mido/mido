.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Parsing MIDI Bytes
------------------

The MIDI protocol is a *binary protocol*. Each message is encoded as a *status*
byte followed by up to three *data* bytes. (Except :term:`SysEx` messages
which can have an arbitrary number of *data* bytes immediately followed by an
EOX status byte.)

.. versionadded:: 1.2 ``mido.Message.from_hex()``

.. note:: To parse a single message you can use the class methods
          ``mido.Message.from_bytes()`` and ``mido.Message.from_hex()``



Mido comes with a *parser* that turns MIDI bytes into messages. You can create
a *parser object* or call one of the *utility functions*::

    >>> mido.parse([0x92, 0x10, 0x20])
    Message('note_on', channel=2, note=16, velocity=32, time=0)

    >>> mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
    [Message('note_on', channel=2, note=16, velocity=32, time=0),
     Message('note_off', channel=2, note=16, velocity=32, time=0)]

These functions are just shortcuts for the full ``Parser`` class. This
is the same parser as used inside input ports to parse incoming messages.
Here are a few examples of how it can be used::

    >>> p = mido.Parser()
    >>> p.feed([0x90, 0x10, 0x20])
    >>> p.pending()
    1
    >>> p.get_message()
    Message('note_on', channel=0, note=16, velocity=32, time=0)

    >>> p.feed_byte(0x90)
    >>> p.feed_byte(0x10)
    >>> p.feed_byte(0x20)
    >>> p.feed([0x80, 0x10, 0x20])
    >>> p.pending()
    2
    >>> p.get_message()
    Message('note_on', channel=0, note=16, velocity=32, time=0)
    >>> p.get_message()
    Message('note_off', channel=0, note=16, velocity=32, time=0)

``feed()`` accepts any iterable that generates integers in 0..255. The
parser will skip and stray status bytes or data bytes, so you can
safely feed it random data and see what comes out the other end.

``get_message()`` will return ``None`` if there are no messages ready
to be gotten.

You can also fetch parsed messages out of the parser by iterating over
it::

    >>> p.feed([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
    >>> for message in p:
    ...    print(message)
    note_on channel=2 note=16 velocity=32 time=0
    note_off channel=2 note=16 velocity=32 time=0

The messages are available in ``p.messages`` (a ``collections.deque``).
