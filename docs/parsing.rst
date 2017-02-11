Parsing MIDI Bytes
==================

MIDI is a binary protocol. Each each message is encoded as a status byte
followed by up to three data bytes. (Sysex messages can have any number of
data bytes and use a stop byte instead.)

.. note:: To parse a single message you can use the class methods
          ``mido.Message.from_bytes()`` and
          ``mido.Message.from_hex()`` (new in 1.2).

Mido comes with a parser that turns MIDI bytes into messages. You can create a parser object, or call one of the utility functions::

    >>> mido.parse([0x92, 0x10, 0x20])
    <message note_on channel=0 note=16 velocity=32 time=0>

    >>> mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
    [<message note_on channel=2 note=16 velocity=32 time=0>,
     <message note_off channel=2 note=16 velocity=32 time=0>]

These functions are just shortcuts for the full ``Parser`` class. This
is the parser used inside input ports to parse incoming messages.
Here are a few examples of how it can be used::

    >>> p = mido.Parser()
    >>> p.feed([0x90, 0x10, 0x20])
    >>> p.pending()
    1
    >>> p.get_message()
    <message note_on channel=0 note=16 velocity=32 time=0>

    >>> p.feed_byte(0x90)
    >>> p.feed_byte(0x10)
    >>> p.feed_byte(0x20)
    >>> p.feed([0x80, 0x10, 0x20])
    <message note_on channel=0 note=16 velocity=32 time=0>

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

The messages are available in `p.messages` (a `collections.deque`).

For the full table of MIDI binary encoding, see:
`<http://www.midi.org/techspecs/midimessages.php>`_
