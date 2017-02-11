Introduction (Basic Concepts)
=============================

Mido is all about messages and ports.


Messages
--------

Mido allows you to work with MIDI messages as Python objects. To
create a new message::

    >>> from mido import Message
    >>> msg = Message('note_on', note=60)
    >>> msg
    <message note_on channel=0 note=60 velocity=64 time=0>

.. note::

    Mido numbers channels 0 to 15 instead of 1 to 16. This makes them
    easier to work with in Python but you may want to add and subtract
    1 when communicating with the user.

A list of all supported message types and their parameters can be
found in :doc:`message_types`.

The values can now be accessed as attributes::

    >>> msg.type
    'note_on'
    >>> msg.note
    60
    >>> msg.velocity
    64

Attributes are also settable but this should be avoided. It's better
to use ``msg.copy()``::

    >>> msg.copy(note=100, velocity=127)
    <message note_on channel=2 note=100 velocity=127 time=0)

Type and value checks are done when you pass parameters or assign to
attributes, and the appropriate exceptions are raised. This ensures
that the message is always valid.

For more about messages, see :doc:`messages`.


Type and Value Checking
-----------------------

Mido messages come with type and value checking built in::

    >>> import mido
    >>> mido.Message('note_on', channel=2092389483249829834)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/olemb/src/mido/mido/messages/messages.py", line 89, in __init__
        check_msgdict(msgdict)
      File "/home/olemb/src/mido/mido/messages/checks.py", line 100, in check_msgdict
        check_value(name, value)
      File "/home/olemb/src/mido/mido/messages/checks.py", line 87, in check_value
        _CHECKS[name](value)
      File "/home/olemb/src/mido/mido/messages/checks.py", line 17, in check_channel
        raise ValueError('channel must be in range 0..15')
    ValueError: channel must be in range 0..15

This means that the message object is always a valid MIDI message.


Ports
-----

To create an output port and send a message::

    >>> outport = mido.open_output()
    >>> outport.send(msg)

To create an input port and receive a message::

    >>> inport = mido.open_input()
    >>> msg = inport.receive()

.. note::

    Multiple threads can safely send and receive notes on the same
    port.

This will give you the default output and input ports. If you want to
open a specific port, you will need its name. To get a list of all
available input ports::

    >>> mido.get_input_names()
    ['Midi Through Port-0', 'SH-201', 'Integra-7']
    >>> inport = mido.open_input('SH-201')

All Mido ports can be used with the ``with`` statement, which will
close the port for you::

    with mido.open_input('SH-201') as inport:
        ...

To iterate through all incoming messages::

    for msg in inport:
        ...

You can also receive and iterate over messages in a non-blocking
way.

For more about ports, see :doc:`ports`.


All Ports are Ports
-------------------

The input and output ports used above are device ports, which
communicate with a (physical or virtual) MIDI device.

Other port types include:

* ``MultiPort``, which wraps around a set of ports and allow you to send to all of them or receive from all of them as if they were one.

* ``SocketPort``, which communicates with another port over a TCP/IP (network) connection.

* ``IOPort``, which wraps around an input and an output port and allows you to send and receive messages as if the two were the same port.

Ports of all types look and behave the same way, so they can be used
interchangeably.

It's easy to write new port types. See :doc:`implementing_ports`.


Virtual Ports
-------------

Virtual ports allow you to create new ports that other applications
can connect to::

    with mido.open_input('New Port', virtual=True) as inport:
        for message in inport:
            print(message)

The port should now appear to other applications as "New Port".

Unfortunately virtual ports are not supported by PortMidi and Pygame
so this only works with RtMidi.


Parsing MIDI Bytes
------------------

Mido comes with a parser that allows you to turn bytes into
messages. You can create a new parser::

    >>> p = mido.Parser()
    >>> p.feed([0x90, 0x40])
    >>> p.feed_byte(0x60)

You can then fetch messages out of the parser::

    >>> p.pending()
    1
    >>> for message in p:
    ...    print(message)
    ...
    note_on channel=0 note=64 velocity=96 time=0

For more on parsers and parsing see :doc:`parsing`.

You can also create a message from bytes using class methods (new in
1.2):

.. code-block:: python

   msg1 = mido.Message.from_bytes([0x90, 0x40, 0x60])
   msg2 = mido.Message.from_hex('90, 40 60')

The bytes must contain exactly one complete message. If not
``ValueError`` is raised.


Backends
--------

Mido comes with backends for RtMidi and PortMidi and Pygame. The
default is RtMidi. You can select another backend or even use multiple
backends at the same time. For more on this, see :doc:`backends/index`.
