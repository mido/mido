Adding New Port Types
======================

Mido comes with support for PortMidi built in, and experimental
support for RtMidi through the python-rtmidi package. If you want to
use some other library or system, like say PyGame, you can write write
custom ports.

There are two ways of adding new port types to Mido.


Duck Typing
------------

The simplest way is to just create an object that has the methods
that you know will be called, for example::

    class PrintPort:
        """Port that prints out messages instead of sending them."""

        def send(self, message):
            print(message)

    port = PrintPort()
    port.send(mido.Message('note_on')


Subclassing
------------

If you want the full range of behaviour, you can subclass the abstract
port classes in ``mido.ports``::

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

        def _get_device_type(self):
            ... A text representation of the type of device,
            ... for example 'CoreMidi' or 'ALSA'. This is
            ... used by __repr__(). Defaults to 'Unknown'.
            return 'CoreMidi'  # For example.


    class Input(PortCommon, BaseInput):
        def _pending(self):
            ... Check for new messages, feed them
            ... to the parser and return how many messages
            ... are now available.

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

See ``mido.portmidi.py`` and ``extras/mido_rtmidi.py`` for full examples.
