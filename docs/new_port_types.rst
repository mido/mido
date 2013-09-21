Writing new Port Types and Backends
===================================

The Mido port API allows you to write new ports to do practically
anything.


Writing a new Port class
------------------------

``mido.ports`` defines base classes that you can use to create your
new port type: ``BaseInput``, ``BaseOutput`` and ``BaseIOPort``.

The base ports define public and private versions of the core methods,
where the public one calls the private one. Overriding only one to
four of these private methods will give you the full port API. The
methods are ``_open()``, ``_close()``, ``_send()`` and ``_pending()``.

Here is an example of a new output port class::

    from mido.ports import BaseOutput

    class PrintPort(BaseOutput):
        def _send(message):
            print(message)

That's all you need to write. The public send method will check if the
message is a ``Message`` object and if the port is open and raise the
correct exceptions. Then it will call ``_send()``. It also provides
the doc string.

If you want your port to support both input and output, you can use
``BaseIOPort``.


Attributes
^^^^^^^^^^

``name``

    The name of the port as as unicode string or None. Set by
    ``__init__()``. The value is device specific and does not have to
    be unique.

``closed``

    True if the port is closed.

``_messages``

    This is a ``collections.deque`` of messages that have been read and
    are ready to be received.

``_device_type`` (Optional.)

    If this attribute exists, it's a string which will be used in
    ``__repr__()``. If it doesn't exist, the class name will be used
    instead.


Overridable Methods
^^^^^^^^^^^^^^^^^^^^

``_open(self)``, ``_open(self, **kwargs)``

    Is called by ``__init__()`` and is responsible for actually opening
    the device or intializing the internal state of the object. The
    name that was passed to ``__init__()`` will already be assigned to
    ``self.name`` while all other keyword arguments arrive here.

    Ports derived from ``BaseInput`` will also a ``self._parser`` and
    ``self._messages``.  ``self._messages`` is a shortcut for as
    ``self._parser._parsed_messages``.

    If you want more control over initialization you can override
    ``__init__()`` instead.

    If an error occurs while opening the device, ``IOError`` should be raised.

``_close(self):``

    Called by ``close()``. Closes the device or frees any resources
    used by the object. This will only be called if the port is still
    open.

    If an error occurs, ``IOError`` should be raised.

``_send(self, message):``

    Called by ``send()``. Will not be called if the port is closed.

    If an error occurs, ``IOError`` should be raised.

``_receive(block=True)``

    Called by ``receive()``, ``pending()``, ``__iter__()`` and
    ``iter_pending()``.

    Will only be called if ``_messages`` is empty.

    Reads messages from the device and feeds them to the parser (or
    inserts them directly into ._messages). Always returns None.

    If ``block=True``, reads messages from the device in a blocking
    way until ._messages is non-empty, and then returns. (If there is
    no way to read from the device in a blocking way, you can return
    after polling the device, and the caller will take care of the
    blocking.)

    If ``block=False``, go in a loop and read data from the device
    until ``_messages`` is non-empty, the return ``None``.

    Do not call ``pending()`` from inside here, since it calls
    you. Use ``len(self._messages)`` instead.


Writing a New Backend
---------------------

Mido comes with backends for PortMidi, python-rtmidi and pygame.midi,
but you can easily add your own.

A backend is a Python module with one or more of these::

    Input -- an input port class
    Output -- an output port class
    IOPort -- an I/O port class
    get_devices() -- returns a list of devices

Once written, the backend can be used by setting the environment
variable ``MIDO_BACKEND`` or by calling ``mido.set_backend()``. In
both cases, the path of the module is used.

``Input``

   And input class for ``open_input()``. This is only required if the
   backend supports input.

``Output``

   And output class for ``open_output()``. This is only required if the
   backend supports output.

``IOPort``

   An I/O port class for ``open_ioport()``. If this is not found,
   ``open_ioport()`` will return ``mido.ports.IOPort(Input(),
   Output())``.

``get_devices()``

   Returns a list of devices, where each device is dictionary with at
   least these three values::

      {
        'name': 'Some MIDI Input Port',
        'is_input': True,
        'is_output': False,
      }

   These are used to build return values for ``get_input_names()`` etc..
   This function will also be available to the user directly.

For examples, see ``mido/backends/``.
