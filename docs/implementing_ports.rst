Writing a New Port
==================

The Mido port API allows you to write new ports to do practically
anything.

A new port type can be defined by subclassing one of the base classes
and overriding one or more methods. Here's an example::

    from mido.ports import BaseOutput

    class PrintPort(BaseOutput):
        def _send(message):
            print(message)

    >>> port = PrintPort()
    >>> port.send(msg)
    note_on channel=0 note=0 velocity=64 time=0

``_send()`` will be called by ``send()``, and is responsible for
actually sending the message somewhere (or in this case print it out).


Overridable Methods
-------------------

There are four overridable methods (all of them default to doing
nothing)::

``_open(self, **kwargs)``

    Should do whatever is necessary to initialize the port (for
    example opening a MIDI device.)

    Called by ``__init__()``. The ``name`` attribute is already
    set when ``_open()`` is called, but you will get the rest of
    the keyword arguments.

    If your port takes a different set of arguments or has other
    special needs, you can override ``__init__()`` instead.

``_close(self)``

    Should clean up whatever resources the port has allocated (such as
    closing a MIDI device).

    Called by ``close()`` if the port is not already closed. 

``_send(self, message)``

    (Output ports only.)

    Should send the message (or do whatever else that makes sense).

    Called by ``send()`` if the port is open and the message is a Mido
    message. (You don't need any type checking here.)

    Raise IOError if something goes wrong.

``_receive(self, block=True)``

    (Input ports only.)

    Should poll the device for available data and feed it to the
    parser.

    Should not return anything. The caller will take care of this, and
    anything you return here will be ignored.

    Is called by various input port methods, like ``receive()`` and
    ``pending()``. The caller takes care of blocking and various error
    situations, so all you need to do is to feed data into the parser.

    If ``block == True`` and the device supports blocking reads, you
    can loop and read until there is a message in ``_messages``. See
    the seconds example below.

    Raise IOError if something goes wrong.

Each method corresponds to the public method of the same name, and
will be called by that method. The outer method will take care of many
things, so the inner method only needs to do the very minimum. The
outer method also provides the doc string, so you don't have to worry
about that.

The base classes are ``BaseInput``, ``BaseOutput`` and ``BaseIOPort``
(which is a subclass of the other two.)


Examples
--------

An full example of a device port for the imaginary MIDI library
``fjopp``::

    import fjopp
    from mido.ports import BaseIOPort

    # This defines an I/O port.
    class FjoppPort(BaseIOPort):
        def _open(self, **kwargs):
	    self._device = fjopp.open_device(self.name)

	def _close(self):
            self._device.close()

        def _send(self, message):
            self.device.write(message.bytes())

        def _receive(self, block=True):
            while True:
	        data = self.device.read()
	        if data:
	            self._parser.feed(data)
                else:
                    return

If ``fjopp`` supports blocking read, you can do this to actually block
on the device instead of letting ``receive()`` and friends poll and
wait for you::

    def _receive(self, block=True):
        if block:
            # Actually block on the device.
	    # (``read_blocking()`` will always return some data.)
	    while not ``self._messages``:
	        data = self._device.read_blocking()
		self._parser.feed(data)
        else:
	    # Non-blocking read like above.
            while True:
	        data = self.device.read()
		if data:
		     self._parser.feed(data)

This can be used for any kind of port that wants to block on a pipe,
an socket or another input source. Note that Mido will still use
polling and waiting when receiving from multiple ports (for example in
a ``MultiPort``).

If you want separate input and output classes, but the ``_open()`` and
``_close()`` methods have a lot in common, you can implement this
using a mix-in.

Sometimes it's useful to know inside the methods whether the port
supports input or output. The way to do this is to check for the
methods ```send()`` and ``receive()``, for example::

    def _open(self, **kwargs):
        if hasattr(self, 'send'):
	    # This is an output port.

        if hasattr(self, 'receive'):
            # This is an input port.

        if hasattr(self, 'send') and hasattr(self, 'receive'):
            # This is an I/O port.


Attributes
----------

A port has some attributes that can be useful inside your methods.

``name``

    The name of the port. The value is device specific and does not
    have to be unique. It can have any value, but must be a string or
    ``None``.

    This is set by ``__init__()``.

``closed``

    True if the port is closed. You don't have to worry about this
    inside your methods.

``_messages``

    This is a ``collections.deque`` of messages that have been read
    and are ready to be received. This is a shortcut to
    ``_parser.parsed_messages``.

``_device_type`` (Optional.)

    If this attribute exists, it's a string which will be used in
    ``__repr__()``. If it doesn't exist, the class name will be used
    instead.
