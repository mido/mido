Tutorial
=========

Creating Messages
------------------

Mido allows you to work with MIDI messages as Python objects. To
create a new message, you can do:

.. code:: python

    >>> import mido
    >>> 
    >>> mido.new('note_on', note=60, velocity=100)
    <note_on message channel=0, note=60, velocity=100, time=0>

or you can use shortcuts:

.. code:: python

    >>> from mido.shortcuts import *
    >>> 
    >>> note_on(note=60, velocity=100)
    <note_on message channel=0, note=60, velocity=100, time=0>

These two methods are equivalent, and which one to use is up to
you. In this tutorial, we will use the shortcuts to make the examples
a little easier to read.

All message parameters are optional, and if not explicitly set, will
default to `0` (or `()` for sysex data):

.. code:: python

    >>> note_on()
    <note_on message channel=0, note=0, velocity=0, time=0>
    >>> sysex()
    <sysex message data=(), time=0>

This means that it's important to remember to pass the `velocity`
parameter for `note_on` messages, or the note will interpreted as a
`note_off` on many devices.

The parameters for each message type are listed in
:doc:`message_types`.


Modifying and Copying Messages
-------------------------------

When you have created a message, the parameters are available as
attributes:

.. code:: python

    >>> n = note_off(channel=1, note=60, velocity=50)
    >>> dir(n)
    [..., 'channel', 'note', 'time', 'type', 'velocity']
    >>> n.type
    'note_on'
    >>> n.channel
    1
    >>> n.note
    60
    >>> n.channel = 2
    >>> n.note = 62
    >>> n
    <note_off message channel=2, note=62, velocity=50, time=0>

You can copy a message, optionally passing keyword arguments to
override attributes:

.. code:: python

    >>> n.copy()  # Make an identical copy.
    <note_on message channel=2, note=62, velocity=50, time=0>
    >>> n.copy(channel=4)
    <note_on message channel=4, note=62, velocity=50, time=0>

This is useful when you pass messages around in a large system, and
you want to keep a copy for yourself while allowing other parts of the
system to modify the original.

Changing the type of a message is not allowed:

.. code:: python

    >>> n.type = 'note_off'
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "mido/messages.py", line 320, in __setattr__
        raise AttributeError('{} attribute is read only'.format(name))
    AttributeError: type attribute is read only
    >>> n.copy(type='note_off')
    (There is currently a bug here: 'type' is allowd as an argument,
    but it is ignored.)


Comparing Messages
-------------------

You can compare two messages to see if they are identical:

.. code:: python

    >>> n == n.copy()
    True
    >>> n == n.copy(note=100)
    False
    >>> note_on() == note_off()
    False

The `time` parameter (see below) is ignored when comparing messages:

.. code:: python

    >>> n == n.copy(time=10000)

This allows you to compare messages that come from different sources
and have different time stamps. If you want to include time in the comparison,
you can do:

.. code:: python

    >>> a = note_on(time=2)
    >>> b = note_on(time=3)
    >>> a == b
    True
    >>> (a, a.time) == (b, b.time)
    False


System Exclusive (sysex) Messages
----------------------------------

Sysex messages have a `data` parameter, which is a sequence of bytes.
The `data` parameter takes any object that generates bytes when
iterated over. This is converted internally into a tuple of integers:

.. code:: python

    >>> sysex()
    <sysex message data=(), time=0>
    >>> sysex(data=[1, 2, 3])
    <sysex message data=(1, 2, 3), time=0>
    >>> sysex(data=bytearray('abc'))
    <sysex message data=(97, 98, 99), time=0>

Sysex messages inlude the `sysex_end` byte when sent and received, so
while there is a `sysex_end` message type, it is never used:

.. code:: python

    >>> s = sysex(data=[1, 2, 3])
    >>> s.hex()
    'F0 01 02 03 F7'


Time
-----

All messages also have an extra parameter `time`, which you can use
for anything you want. Typically this is used to tag messages with
time when storing them in files or sending them around in the
system. `time` can have any value as long as it's a `float` or an `int`.

`copy()` will copy the `time` attribute.


Opening Ports
--------------

There are three types of ports in Mido: input ports, output ports and
I/O ports. They are created with:

.. code:: python

    mido.input(name=None)
    mido.output(name=None)
    mido.ioport(name=None)

(`mido.ioport` will return a port which is a thin wrapper around an
input port and an output port, and allows you to use the methods of
both. This can be used for two-way communication with a device.

You can pass the name of the port, or leave it out to open the default
port.

.. code:: python

    mido.input('SH-201')  # Open the port 'SH-201'.
    mido.input()  # Open the default input port.

To get a list of names of available ports, you can call one of these
functions:

.. code:: python

    >>> >>> mido.input_names()
    ['Midi Through Port-0', 'SH-201']
    >>> mido.output_names()
    ['Midi Through Port-0', 'SH-201']
    >>> mido.ioport_names()
    ['Midi Through Port-0', 'SH-201']

In this case, all ports can be opened as inputs and
outputs. (*Important:* If a port is open, it will still be listed
here.)

    >>> mido.input()
    <open input port 'Midi Through Port-0' (ALSA)>


Closing Ports
--------------

A port can be closed by calling the `close()` method:

.. code:: python

    port.close()

but often it is better to use the `with` statement, which will close
the block automatically when the block is over:

.. code:: python

    with mido.output() as port:
        ...

The `closed` attribute will be `True` if the port is closed.


Sending Messages
-----------------

Messages can be sent on output or I/O ports by calling the `send()`
method:

.. code:: python

    port.send(pitchwheel(channel=2, pitch=4000))

The message will be sent immediately.


Receiving Messages
-------------------

There are several different ways to receive messages. The basic one is
to call `receive()`:

.. code:: python

    message = port.receive()

This will block until a message arrives on the port. If you want to
receive messages in a loop, you can do:

.. code:: python

    for message in port:
        ...

If you don't want to block, you can use `pending()` to see how many
messages are available:

.. code:: python

    >>> port.pending()
    2
    >>> port.receive()
    <note_on message channel=2, note=60, velocity=50, time=0>
    >>> port.receive()
    <note_on message channel=2, note=72, velocity=50, time=0>
    >>> port.receive()
        *** blocks until the next message arrives ***

It is often easier to use `iter_pending()`:

.. code:: python

    while 1:
        for message in port.iter_pending():
            ... # Do something with message.

        ... Do other stuff.

Messages will be queued up inside the port object until you call
`receive()` or `iter_pending()`.

If you want to receive messages from multiple ports, you can use
`ports.multi_receive()`:

.. code:: python

    from mido.ports import multi_receive
    
    while 1:
        for message in multi_receive([port1, port2, port3]):
            ...

The ports are checked in random order to ensure fairness. There is
also a non-blocking version of this function:

.. code:: python

    while 1:
        for message in multi_iter_pending([port1, port2, port3]):
            ...
