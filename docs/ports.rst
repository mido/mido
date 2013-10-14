Ports
======

A Mido port is an object that can send or receive messages (or both).

You can open a port by calling one of the open methods, for example::

    >>> inport = mido.open_input('SH-201')
    >>> outport = mido.open_output('Integra-7')

Now you can receive messages on the input port and send messages on
the output port::

    >>> msg = inport.receive():
    >>> outport.send(msg)

The message is copied by ``send()``, so you can safely modify your
original message without causing breakage in other parts of the
system.

In this case, the ports are device ports, and are connected to some
sort of (physical or virtual) MIDI device, but a port can be
anything. For example, you can use a ``MultiPort`` receive messages
from multiple ports as if they were one::

    from mido.ports import MultiPort

    ...
    multi = MultiPort([inport1, inport2, inport3])
    for msg in multi:
        print(msg)

This will receive messages from all ports and print them out. Another
example is a socket port, which is a wrapper around a TCP/IP socket.

No matter how the port is implemented internally or what it does, it
will look and behave like any other Mido port, so all kinds of ports
can be used interchangingly.


Common Things
--------------

How to open a port depends on the port type. Device ports (PortMidi,
RtMidi and others defined in backends) are opened with the open
functions, for example::

    port = mido.open_output()

Input and I/O ports (which support both input and output) are opened
with ``open_input()`` and ``open_ioport()`` respectively. If you call
these without a port name like above, you will get the (system
specific) default port. You can override this by setting the
``MIDO_DEFAULT_OUTPUT`` etc. environment variables.

To get a list of available ports, you can do::

    >>> mido.output_port_names()
    ['SH-201', 'Integra-7']

and then::

    >>> port = mido.open_output('Integra-7')

There are corresponding function for input and I/O ports.

To learn how to open other kinds of ports, see the documentation for
the port type in question.

The port name is available in ``port.name``.

To close a port, call::

    port.close()

or use the ``with`` statement to have the port closed automatically::

    with mido.open_input() as port:
        for message in port:
            do_something_with(message)

You can check if the port is closed with::

    if port.closed:
        print("Yup, it's closed.")

If the port is already closed, calling ``close()`` will simply do nothing.


Output Ports
-------------

Output ports basically have only one method::

    outport.send(message)

This will send the message immediately. (Well, the port can choose to
do whatever it wants with the message, but at least it's sent.)

There are also a couple of utility methods::

    outport.reset()

This will send "all notes off" and "reset all controllers" on every
channel. This is used to reset everything to the default state, for
example after playing back a song or messing around with controllers.

If you pass ``autoreset=True`` to the constructor, ``reset()`` will be
called when the port closes::

    with mido.open_output('Integra-7') as outport:
        for msg in inport:
            outport.send(msg)
    # reset() is called here 

    outport.close()  # or here

Sometimes notes hang because a ``note_off`` has not been sent. To
(abruptly) stop all sounding notes, you can call:

    outport.panic()

This will not reset controllers. Unlike ``reset()``, the notes will
not be turned off gracefully, but will stop immediately with no regard
to decay time.


Input Ports
------------

To receive a message::

    msg = port.receive()

This will block until a message arrives. To get a message only if one
is available, you can use::

    msg = port.receive(block=False)

which will return ``None`` if no message is available.

The ``pending()`` method will return the number of messages that are
waiting to be received, so you can do::

    while port.pending():
        msg = port.receive()
        print(msg)

but it's usually easier to just to::

    for msg in port.iter_pending():
        print(msg)

You can also loop through messages in a blocking way::

    for msg in port:
        print(msg)

This will give you all messages as they arrive on the port until the
port closes. (So far only socket ports actually close by
themselves. This happens if the other end disconnects.)

Input ports take an optional ``callback`` argument::

    def print_message(message):
        print(message)

    port = mido.open_input('SH-201', callback=print_message)

The function will be called with every message that arrives on the
port. This is currently only implemented PortMidi and RtMidi ports.

You can change the callback function later by setting the ``callback``
attribute::

    port.callback = print_message
    ...
    port.callback = None

If ``callback`` is set to ``None``, no function will be called. This
can be used to temporarily (or permanently) turn off message
reception.

The ``receive`` methods can not be used if a callback is set.


Port API
---------

Common Methods and Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``close()``

Close the port. If the port is already closed this will simply do
nothing.

``name``

Name of the port or None.


``closed``

True if the port is closed.


Output Port Methods
^^^^^^^^^^^^^^^^^^^^

``send(message)``

Send a message.


``reset()``

Sends "all notes off" and "reset all controllers on all channels.


``panic()``

Sends "all sounds off" on all channels. This will abruptly end all
sounding notes.


Input Port Methods
^^^^^^^^^^^^^^^^^^^

``receive(block=True)``

Receive a message. This will return a message. If ``block=False``,
``None`` is returned if no message is available.


``pending()``

Returns the number of messages waiting to be received.


``iter_pending()``

Iterates through pending messages.


``__iter__()``

Iterates through messages as they arrive on the port until the port
closes.


