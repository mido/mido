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

If you're implementing a new port type or support for a binary file
format, you may need to parse binary MIDI messages. Mido has a few
functions and one class that make this easy.

To parse a single message::

    >>> mido.parse([0x92, 0x10, 0x20])
    <message note_on channel=0, note=16, velocity=32, time=0>

``parse()`` will only return the first message in the byte stream. To
get all messages as a list, use ``parse_all()``::

    >>> mido.parse_all([0x92, 0x10, 0x20, 0x82, 0x10, 0x20])
    [<message note_on channel=2, note=16, velocity=32, time=0>,
     <message note_off channel=2, note=16, velocity=32, time=0>]

The functions are just shortcuts for the full ``Parser`` class. This
is the parser used inside input ports to parse incoming messages.
Here are a few examples of how it can be used::

    >>> p = mido.Parser()
    >>> p.feed([0x90, 0x10, 0x20])
    >>> p.pending()
    1
    >>> p.get_message()
    <message note_on channel=0, note=16, velocity=32, time=0>

    >>> p.feed_byte(0x90)
    >>> p.feed_byte(0x10)
    >>> p.feed_byte(0x20)
    >>> p.feed([0x80, 0x10, 0x20])
    <message note_on channel=0, note=16, velocity=32, time=0>

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
