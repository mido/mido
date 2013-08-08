Parsing and Encoding Messages
==============================

MIDI is a binary protocol. Each each message is encoded as a status byte
followed by up to three data bytes. (Sysex messages can have any number of
data bytes and use a stop byte instead.)

Messages can be encoded by calling one of these methods::

    >>> n = Message('note_on', channel=2, note=60, velocity=100, time=3)
    >>> n.bytes()
    [146, 60, 100]
    >>> n.hex()
    '92 3C 64'
    >>> n.hex(sep='-')
    '92-3C-64'
    >>> n.bin()
    bytearray(b'\x92<d')

For the full table of MIDI binary encoding, see:
`<http://www.midi.org/techspecs/midimessages.php>`_


Parsing Messages
-----------------

Mido comes with a parser that parses byte streams. Each input port
comes with a parser built in (available internally as ``self._parser``).

If you want to parse data from another source, you can create your own parser
object::

    >>> p = mido.Parser()

You can then feed it bytes individually or in chunks::

    >>> p.feed_byte(0x90)
    >>> p.feed_byte(0x10)
    >>> p.feed_byte(0x20)
    >>> p.feed([0x80, 0x10, 0x20])

You can then fetch parsed messages out of the parser one by one or by
iteration::

    >>> p.pending()
    2
    >>> p.get_message()
    <message note_on channel=0, note=16, velocity=32, time=0>
    >>> for message in p:
    ...     print(message)
    <message note_off channel=0, note=16, velocity=32, time=0>

`feed()` accepts any iterable that generates integers in 0..255.
The parser will skip and stray status bytes or data bytes, so you can
safely feed it random data and see what comes out the other end.

There are a couple of shortcuts for when you only want to parse one message
or a short list of bytes::

    >>> mido.parse([0x92, 0x10, 0x20])
    <message note_on channel=0, note=16, velocity=32, time=0>

    >>> mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
    <message note_on channel=0, note=16, velocity=32, time=0>
    <message note_off channel=0, note=16, velocity=32, time=0>

The messages will stay in an internal queue intil you pull them out
with `get_message()` or `for message in parser:`.
