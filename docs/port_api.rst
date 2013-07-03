Port API and Custom Ports
==========================

Mido currently only supportes PortMidi, but if you want to use it with
another MIDI library you can write your own custom port classes. These
need not be registered with Mido before use.

You only need to implement what you intend to use. Provided you only
need to use `send()`, this is a valid port:

.. code:: python

    class MyPrintOutput:
        def send(self, message):
            print(message)

    myport = MyPrintOutput()

    for msg in mido.input():
        myport.send(msg)

The full port API is listed below. (I considering adding some classes
in `mido.ports` that you can subclass to make things a little easier.)

Have a look at `mido.portmidi` for an example of how things can be
done.


Common Methods and Attributes
-----------------------------

.. py:attribute:: name

   Name of the port. (If this is the default port, the backend will
   have retrieved the name and assigned it to `self.name`, so this
   will never be `None`.


.. py:attribute:: closed

   `True` if the port is closed.


.. py:function:: __init__(name=None)

   Open a named port. If name is `None`, the default port is
   opened. (What the default port is depends on the backend being
   used.)


.. py:function:: close()

   Close the port. This is called by `__del__()` when the port is deleted,
   garbage collected (todo: is this true?) or goes out of scope.


.. py:function:: __del__()

   Calls .close() if `closed` is not `True`.


.. py:function:: __enter__()

   Enter context manager. Typically implemented as:

.. code:: python

    def __enter__(self):
        return self


.. py:function:: __exit__()

   Exit the context manager. Typically implemented as:

.. code:: python

    def __exit__(self, type, value, traceback):
        return False



Methods Specific to Input Ports
--------------------------------

.. code:: python

.. py:function:: recieve()

    Blocks until there is a message, and then returns it. Non-blocking
    receive by first calling `pending()` to see how many messages are
    ready to be received, or by iterating through `iter_pending()`.


.. py:function:: pending()

    Returns the number of messages that have arrived and can safely be
    received with `receive()`.

    This is good place to actually read data from the underlying device.


.. py:function:: iter_pending()

    Iterate through pending messages.


.. py:function:: __iter__()

    Iterate through all messages that arrive on the ports. This will
    block until there is a new message, so it is typically used like this:

.. code:: python

    for message in mido.input():
        print(message)
        
        if we_need_to_exit():
            break

    
Methods Specific to Output Ports
---------------------------------

.. code:: python

.. py:function:: send(message)

   Send a message on the port. The message is sent right away.

   How interleaving how sysex and realtime messages is handled is up
   to the implementation, or the underlying MIDI library.
