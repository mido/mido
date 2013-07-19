Parsing and Encoding Messages
==============================

MIDI is a binary protocol, which means when sending a message to a
device, it is encoded as one or more consecutive bytes.

The input and output ports will decode and encode messages for you, so
unless you're implementing a new MIDI backend or a file reader /
writer, there is little use for this.

Message objects have a few methods that make encoding easy::

    >>> n = Message('note_on', channel=2, note=60, velocity=100, time=3)
    >>> n.bytes()
    [146, 60, 100]
    >>> n.hex()
    '92 3C 64'
    >>> n.hex(sep='-')
    '92-3C-64'
    >>> n.bin()
    bytearray(b'\x92<d')

System Exclusive messages include the end byte (0xf7)::

    >>> Message('sysex', data=[1, 2, 3]).hex()
    'F0 01 02 03 F7'

This means, the sysex_end() message type is needed.

For the full table of MIDI binary encoding, see:
`<http://www.midi.org/techspecs/midimessages.php>`_


Parsing Messages
-----------------

If you're implementing a new port type or support for a binary file
format, you may need to parse binary MIDI messages. Mido has a few
functions and one class that make this easy.

To parse a single message::

    >>> mido.parse([0x92, 0x10, 0x20])
    <note_on message channel=0, note=16, velocity=32, time=0>

`parse()` will only return the first message in the byte stream. To
get all messages, use `parse_all()`.

The functions are just shortcuts for the full `Parser` class. This is
the parser used inside input ports to parse incoming messages. Here
are a few examples of how it can be used::

    >>> p = mido.Parser()
    >>> p.feed([0x90, 0x10, 0x20])
    >>> p.pending()
    1
    >>> p.get_message()
    <note_on message channel=0, note=16, velocity=32, time=0>
    >>> p.feed_byte(0x90)
    >>> p.feed_byte(0x10)
    >>> p.feed_byte(0x20)
    >>> p.get_message()
    <note_on message channel=0, note=16, velocity=32, time=0>

`get_message()` will return `None` if there are no messages ready to
be gotten.

`feed()` accepts any iterable that generates integers in 0..255. This
includes::

    p.feed([0x90, 0x10, 0x20])
    p.feed((i for i in range(256)))

The messages will stay in an internal queue intil you pull them out
with `get_message()` or `for message in parser:`.

The parser will skip and stray status bytes or data bytes, so you can
safely feed it random data and see what comes out the other end.
