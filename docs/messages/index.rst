.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Messages
========

A Mido message is a Python object with methods and attributes. The
attributes will vary depending on message type.

To create a new message::

    >>> mido.Message('note_on')
    Message('note_on', channel=0, note=0, velocity=64, time=0)

You can pass attributes as keyword arguments::

    >>> mido.Message('note_on', note=100, velocity=3, time=6.2)
    Message('note_on', channel=0, note=100, velocity=3, time=6.2)

All attributes will default to ``0``.
The exceptions are ``velocity``, which defaults to ``64`` (middle velocity)
and ``data`` which defaults to ``()``.

You can set and get attributes as you would expect::

    >>> msg = mido.Message('note_on')
    >>> msg.note
    0

The ``type`` attribute can be used to determine message type::

    >>> msg.type
    'note_on'

Attributes are also settable but it's always better to use
``msg.copy()``::

    >>> msg.copy(note=99, time=100.0)
    Message('note_on', channel=0, note=99, velocity=64, time=100.0)

.. note:: Mido always makes a copy of messages instead of modifying
          them so if you do the same you have immutable messages in
          practice. (Third party libraries may not follow the same
          rule.)

.. note:: :doc:`frozen` are a variant of messages that are
          hashable and can be used as dictionary keys. They are also
          safe from tampering by third party libraries. You can freely
          convert between the two and use frozen messages wherever
          normal messages are allowed.

Mido supports all message types defined by the :term:`MIDI` standard. For a
full list of messages and their attributes, see :doc:`../message_types`.


Control Changes
---------------

.. code-block:: python

    if msg.is_cc():
        print('Control change message received')

    if msg.is_cc(7):
        print('Volume changed to', msg.value)


Converting To & From Bytes
--------------------------

To Bytes
^^^^^^^^

You can convert a message to :term:`MIDI` ``bytes`` with one of these methods:

    >>> msg = mido.Message('note_on')
    >>> msg
    Message('note_on', channel=0, note=0, velocity=64, time=0)
    >>> msg.bytes()
    [144, 0, 64]
    >>> msg.bin()
    bytearray(b'\x90\x00@')
    >>> msg.hex()
    '90 00 40'


From Bytes
^^^^^^^^^^

You can turn ``bytes`` back into messages with the :doc:`parser <parsing>`.

.. versionadded:: 1.2

You can also create a message from ``bytes`` using class methods:

.. code-block:: python

   msg1 = mido.Message.from_bytes([0x90, 0x40, 0x60])
   msg2 = mido.Message.from_hex('90, 40 60')

The ``bytes`` must contain exactly one complete message. If not
``ValueError`` is raised.



The Time Attribute
------------------

Each message has a ``time`` attribute, which can be set to any value
of type ``int`` or ``float``.

Some parts of Mido use the attribute for special purposes. In ``MIDI file``
tracks, it is used as delta time (in :term:`ticks`), and it must be a
non-negative integer.

In other parts of Mido, this value is ignored.

.. versionchanged:: 1.1.18

    In earlier versions, the ``time`` attribute was not included in
    comparisons. If you want the old behavior the easiest way is
    ``msg1.bytes() == msg2.bytes()``.

To sort messages on time you can do::

    messages.sort(key=lambda message: message.time)

or::

    import operator

    messages.sort(key=operator.attrgetter('time'))


System Exclusive Messages
-------------------------

:term:`System Exclusive` (aka :term:`SysEx`) messages are used to send device
specific data. The ``data`` attribute is a tuple of data bytes which serves as
the payload of the message::

    >>> msg = Message('sysex', data=[1, 2, 3])
    >>> msg
    Message('sysex', data=(1, 2, 3), time=0)
    >>> msg.hex()
    'F0 01 02 03 F7'

You can also extend the existing data::

   >>> msg = Message('sysex', data=[1, 2, 3])
   >>> msg.data += [4, 5]
   >>> msg.data += [6, 7, 8]
   >>> msg
   Message('sysex', data=(1, 2, 3, 4, 5, 6, 7, 8), time=0)

Any sequence of integers between `0` and `127` is allowed, and type and range
checking is applied to each data byte.

These are all valid::

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
    Message('sysex', data=(65, 66, 67, 68, 69, 70), time=0)


.. include:: frozen.rst

.. include:: parsing.rst

.. include:: serializing.rst
