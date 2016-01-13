Messages
========

A Mido message is a Python object with methods and attributes. The
attributes will vary depending on message type.

To create a new message::

    >>> mido.Message('note_on')
    <message note_on channel=0 note=0 velocity=64 time=0>

You can pass attributes as keyword arguments::

    >>> mido.Message('note_on', note=100, velocity=3, time=6.2)
    <message note_on channel=0 note=100 velocity=3 time=6.2>

All attributes will default to 0. The exceptions are ``velocity``,
which defaults to 64 (middle velocity) and ``data`` which defaults to
``()``.

You can set and get attributes as you would expect::

    >>> msg = mido.Message('note_on')
    >>> msg.note
    0
    >>> msg.note = 100
    >>> msg.note
    100

The ``type`` attribute can be used to determine message type::

    >>> msg.type
    'note_on'

To make a copy of a message, optionally overriding one or more
attributes::

    >>> msg.copy(note=99, time=100.0)
    <message note_on channel=0 note=99 velocity=64 time=100.0>

Mido supports all message types defined by the MIDI standard. For a
full list of messages and their attributes, see :doc:`message_types`.


Comparison
----------

To compare two messages::

    >>> Message('note_on', note=60) == Message('note_on', note=60)
    True
    >>> Message('note_on', note=60) == Message('note_on', note=120)
    False

Messages of different types are never equal::

    >>> Message('note_on') == Message('program_change')
    False

The ``time`` attribute is not included in comparisons::

    >>> a = Message('note_on', time=1)
    >>> b = Message('note_on', time=2)
    >>> a == b
    True

The reason why time is not compared is that it's not regarded as part
of the messages, but rather something that is tagged into it. To
include ``time`` in the comparison you can do::

    >>> a = Message('note_on', time=1)
    >>> b = Message('note_on', time=2)
    >>> (a, a.time) == (b, b.time)
    False

Sort ordering of messages is not defined.


Converting To Bytes
-------------------

You can convert a message to MIDI bytes with one of these methods:

    >>> msg = mido.Message('note_on')
    >>> msg
    <message note_on channel=0 note=0 velocity=64 time=0>
    >>> msg.bytes()
    [144, 0, 64]
    >>> msg.bin()
    bytearray(b'\x90\x00@')
    >>> msg.hex()
    '90 00 40'

You can turn bytes back into messages with the :doc:`parser <parsing>`.


The Time Attribute
------------------

Each message has a ``time`` attribute, which can be set to any value
of type ``int`` or ``float`` (and in Python 2 also ``long``). What you
do with this value is entirely up to you.

Some parts of Mido uses the attribute for special purposes. In MIDI
file tracks, it is used as delta time (in ticks).

The ``time`` attribute is not included in comparisons. (See
"Comparison" above.)

To sort messages on time you can do::

    messages.sort(key=lambda message: message.time)

or::

    import operator

    messages.sort(key=operator.attrgetter('time'))


System Exclusive Messages
-------------------------

System Exclusive (SysEx) messages are used to send device specific
data. The ``data`` attribute is a tuple of data bytes which serves as
the payload of the message::

    >>> msg = Message('sysex', data=[1, 2, 3])
    >>> msg
    <message sysex data=(1, 2, 3) time=0>
    >>> msg.hex()
    'F0 01 02 03 F7'

You can also extend the existing data::

   >>> msg = Message('sysex', data=[1, 2, 3])
   >>> msg.data += [4, 5]
   >>> msg.data += [6, 7, 8]
   >>> msg
   <message sysex data=(1, 2, 3, 4, 5, 6, 7, 8) time=0>

Any sequence of integers is allowed, and type and range checking is
applied to each data byte. These are all valid::

    (65, 66, 67)
    [65, 66, 67]
    (i + 65 for i in range(3))
    (ord(c) for c in 'ABC')
    bytearray(b'ABC')
    b'ABC'  # Python 3 only.

For example::

    >>> msg = Message('sysex', data=bytearray(b'ABC'))
    >>> msg.data += bytearray(b'DEF')
    >>> msg
    <message sysex data=(65, 66, 67, 68, 69, 70) time=0>
