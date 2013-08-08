=======================
 Adding New Port Types
=======================




Subclassing
===========

name

    The name of the port. Must be a unicode string or None. The name
    does not have to be unique. You can choose any name that makes
    sense for your port type. If names don't make sense, just use None.

closed

    True if the port is closed.

_messages

    For input ports.

    This is a ``collections.deque`` of messages that have been read and
    are ready to be received.

_open(self, **kwargs)

    Is called by ``__init__()`` and is responsible for actually opening
    the device or intializing the internal state of the object. The
    name that was passed to ``__init__()`` will already be assigned to
    ``self.name`` while all other keyword arguments arrive here.

    Ports derived from ``BaseInput`` will also a ``self._parser`` and
    ``self._messages``.  ``self._messages`` is a shortcut for as
    ``self._parser._parsed_messages``.

    If you want more control over initialization you can override
    ``__init__`` instead.

_close(self):

    Called by ``close()``. Closes the device or frees any resources
    used by the object. This will only be called if the port is still
    open.

_send(self, message):

    Called by ``send()``. Will not be called if the port is closed.

_pending(self):

    Called by ``pending()``.

    Checks the device for new messages and appends them to
    ``self._messages``. Returns the number of messages now pending. If
    you would just have returned ``len(self._messages)``, you can return
    ``None`` and just let ``pending()`` take care of the return value.

Here is an implementation of a simple I/O port::

    from mido.ports import BaseInput, BaseOutput

    class EchoPort(BaseInput, BaseOutput):
        def __init__(self):
            pass  # This is just here so that we don't take any arguments.

        def _send(self, message):
            self._messages.append(message)            

If you want the full range of behaviour, you can subclass the abstract
port classes in ``mido.ports``. Here's a simple output port::

    from mido.ports import BaseOutput

    class PrintPort(BaseOutput):
        def 

    from mido.ports import BaseInput, BaseOutput

    class PortCommon(object):
        ... Mixin for things that are common to your Input and Output
        ... ports (so you don't need a lot of duplicate code.

        def _open(self, **kwargs): 
            ... This is where you actually # open
            ... the underlying device.
            ...
            ... self.name will be set to the name that was passed
            ... **kwargs will be passed to you by __init__()

        def _close(self):
            ... Close the underlying device.

    class Input(PortCommon, BaseInput):
        def _pending(self):
            ... Check for new messages, feed them
            ... to the parser and return how many messages
            ... are now available.
            ...
            ... Returns the number of available messages.
            ... If it returns None, pending() will return
            ... len(self._messages).

    class Output(PortCommon, BaseOutput):
        def _send(self, message):
            ... Send the message via the underlying device.

The base classes will take care of everything else. You may still
override selected methods if you need to.

All the methods you need to override start with an underscore and is
are called by the corresponding method without an underscore. This
allows the base class to do some type and value checking for you
before calling your implementation specific method. It also means you
don't have to worry about adding doc strings.

See ``mido/backends/``, ``mido.ports.py`` and ``mido/sockets.py`` for
full examples.


Duck Typing
===========

If you know that you'll only use part of the port API, you can make a
quick class without subclassing::

    class PrintPort:
        """Port that prints out messages instead of sending them."""

        def send(self, message):
            print(message)

    port = PrintPort()
    port.send(mido.Message('note_on')

This will behave like an output port.


Writing a New Backend
=====================

Mido comes with backends for PortMidi, python-rtmidi and pygame.midi,
but you can easily add your own. All you need to do is to write a
module with the following::

    Input -- an input class like above (optional)
    Output -- an output class like above (optional
    IOPort -- an I/O port class (if not present, IOPort will be used as
              a wrapper
    get_devices() -- returns a list of devices, as described below

All of these are optional. For example, if the backend only supports
output, you only need ``Output`` and ``get_devices()``.

If ``IOPort`` is left out, Mido will open your ``Input`` and
``Output`` and wrap a ``mido.ports.IOPort`` around them.

``get_devices()`` returns a list of devices, where each device is
dictionary with at least these three values::

    {
      'name': 'Some MIDI Input Port',
      'is_input': True,
      'is_output': False,
    }

These are used to build return values for ``get_input_names()`` etc.,
and the user can access these directly for more fine-grained control.
You can 

Here is a simple backend that implements input and output, but not
``get_devices()``:

    from mido.ports import BaseInput, BaseOutput

    # The Input and Output usually contains almost the same
    # code. A mix-in like this one is a good way to avoid
    # repetition.
    class PortCommon:
        def _open(self, *kwargs):
            # Determine if this is an input or an output.
            is_input = hasattr(self, 'receive')
            ... # Open the port here

        def _close(self):
            self.device.close()  # For example

    class Input(PortCommon, BaseInput):
        def _pending(self):
            # Check device for new messages and feed these
            # to the parser.
            ...

    class Output(PortCommon, BaseOutput):
        def _send(self, message):
            ... # Encode the messages (typically using message.bytes()) and
                # send it to the device.

For more examples, see ``mido/backends/``.
