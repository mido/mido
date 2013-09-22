Quickstart (Some Sort of Tutorial)
===================================

Basics Concepts
----------------

Mido is all about messages and ports.


Messages
---------

Mido allows you to work with MIDI messages as Python objects. To
create a new message::

    >>> from mido import Message
    >>> msg = Message('note_on', note=60)
    >>> msg
    <message note_on channel=0, note=60, velocity=64, time=0)

All message parameters are optional, and will be set to 0 if not
passed. The exception is velocity which defaults to 64.

A list of all supported message types and their parameters can be
found in :doc:`message_types`.

The values can now be accessed as attributes::

    >>> msg.type
    'note_on'
    >>> msg.note
    60
    >>> msg.velocity
    64

All attributes are also settable::

    >>> msg.channel = 2
    >>> msg.note = 122
    <message note_on channel=2, note=122, velocity=64, time=0)

However, you can not change the type of a message.

You can make a copy of a message, optionally overriding one or more
attributes, for example::

    >>> msg.copy(note=100, velocity=127)
    <message note_on channel=2, note=122, velocity=127, time=0)

Type and value checks are done when you pass parameters or assign to
attributes, and the appropriate exceptions are raised. This ensures
that the message is always valid.

More on messages later, but first a bit about ports.


Ports
------

To create an output port and send a message::

    >>> outport = mido.open_output()
    >>> outport.send(msg)

To create an input port and receive a message::

    >>> inport = mido.open_input()
    >>> msg = inport.receive()

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

You can also iterate through incoming messages::

    for msg in inport:
        ...

You can also receive and iterate over messages in a non-blocking
way. There's more about this in the (ports.rst ZZZZZZZZZ) section.


All Ports are Ports
--------------------

The input and output ports used above are device ports. They
communicate with a MIDI device external to the program.

There are many other types of ports, but since they all have exactly
the same API, you can use any kind of port in place of any other kind.

Some examples of non-device ports are:

    * ``IOPort``, which wraps around an input and an output port and
      let's you use them as if they were one port. (You can get such a
      port by calling ``mido.open_ioport()``, which opens the two
      ports for you and returns the wrapper object. This assumes that
      and input and an output port with the same name are avaiable.)

    * ``MultiPort``, which wraps around a list of ports and sends
      all outgoing messages to all ports and receives messages
      from all ports, all as if they were one.

    * ``SocketPort``, which wraps about a TCP/IP socket, and allows
      you to send and receive messages over a network connection.

This code sends every incoming messages to the output ports::

    for msg in inport:
        outport.send(msg)

This will work no matter what kind of port ``inport`` and
``outport``. You can turn outport into a ``MultiPort`` without any
change to this part of the code.

New port types can be easily written by subclassing and overloading
1-4 methods. (See ZZZZZZZZZZZZZ for more about writing new port types.)


The Time Attribute
-------------------

Each message has a ``time`` attribute, which can be set to any value
of type ``int`` or ``float`` (and in Python 2 also ``long``). What you
do with this value is entirely up to you.

Some parts of Mido uses the attribute for special purposes. In MIDI
file tracks, it is used as delta time (in ticks).

*Note*: the ``time`` attribute is not included in comparisons, so if
 you want it included you'll have to do::

    (msg1, msg1.time) == (msg2, msg2.time)


Sysex Messages
---------------

Sytem Exclusive (SysEx) messages are used to send device specific
data. They have one attribute, ``data``, which is the payload of the
message::

    >>> msg = Message('sysex', data=(1, 2, 3))
    >>> msg
    <message sysex data=(1, 2, 3), time=0>

You can pass or set any (finite) iterable. It will be converted to
a tuple::

    >>> msg.data = range(3)
    >>> msg.data
    (0, 1, 2)
