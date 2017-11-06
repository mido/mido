Ports
=====

A Mido port is an object that can send or receive messages (or both).

You can open a port by calling one of the open methods, for example::

    >>> inport = mido.open_input('SH-201')
    >>> outport = mido.open_output('Integra-7')

Now you can receive messages on the input port and send messages on
the output port::

    >>> msg = inport.receive()
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
can be used interchangeably.


.. note:: Sending and receiving messages is thread safe. Opening and
          closing ports and listing port names are not.


Common Things
-------------

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

    >>> mido.get_output_names()
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
------------

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
(abruptly) stop all sounding notes, you can call::

    outport.panic()

This will not reset controllers. Unlike ``reset()``, the notes will
not be turned off gracefully, but will stop immediately with no regard
to decay time.


Input Ports
-----------

To iterate over incoming messages:::

    for msg in port:
        print(msg)

This will iterate over messages as they arrive on the port until the
port closes. (So far only socket ports actually close by
themselves. This happens if the other end disconnects.)

You can also do non-blocking iteration::

    for msg in port.iter_pending():
        print(msg)

This will iterate over all messages that have already arrived. It is
typically used in main loops where you want to do something else while
you wait for messages::

    while True:
        for msg in port.iter_pending():
            print(msg)

        do_other_stuff()

In an event based system like a GUI where you don't write the main
loop you can install a handler that's called periodically. Here's an
example for GTK::

    def callback(self):
        for msg in self.inport:
            print(msg)

    gobject.timeout_add_seconds(timeout, callback)

To get a bit more control you can receive messages one at a time::

    msg = port.receive()

This will block until a message arrives. To get a message only if one
is available, you can use `poll()`::

    msg = port.poll()

This will return ``None`` if no message is available.

.. note:: There used to be a ``pending()`` method which returned the
          number of pending messages. It was removed in 1.2.0 for
          three reasons:
          
          * with ``poll()`` and ``iter_pending()`` it is no longer
            necessary

          * it was unreliable when multithreading and for some ports
            it doesn't even make sense

          * it made the internal method API confusing. `_send()` sends
            a message so `_receive()` should receive a message.


Callbacks
---------

Instead of reading from the port you can install a callback function
which will be called for every message that arrives.

Here's a simple callback function::

    def print_message(message):
        print(message)

To install the callback you can either pass it when you create the
port or later by setting the ``callback`` attribute::

    port = mido.open_input(callback=print_message)
    port.callback = print_message
    ...
    port.callback = another_function

.. note::

    Since the callback runs in a different thread you may need to use
    locks or other synchronization mechanisms to keep your main program and
    the callback from stepping on each other's toes.

Calling ``receive()``, ``__iter__()``, or ``iter_pending()`` on a port
with a callback will raise an exception::

    ValueError: a callback is set for this port

To clear the callback::

    port.callback = None

This will return the port to normal.


Port API
--------

Common Methods and Attributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

``close()``

Close the port. If the port is already closed this will simply do
nothing.

``name``

Name of the port or None.


``closed``

True if the port is closed.


Output Port Methods
^^^^^^^^^^^^^^^^^^^

``send(message)``

Send a message.


``reset()``

Sends "all notes off" and "reset all controllers on all channels.


``panic()``

Sends "all sounds off" on all channels. This will abruptly end all
sounding notes.


Input Port Methods
^^^^^^^^^^^^^^^^^^

``receive(block=True)``

Receive a message. This will block until it returns a message. If
``block=True`` is passed it will instead return ``None`` if there is
no message.


``poll()``

Returns a message, or ``None`` if there are no pending messages.


``iter_pending()``

Iterates through pending messages.


``__iter__()``

Iterates through messages as they arrive on the port until the port
closes.
