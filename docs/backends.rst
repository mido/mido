=========
Backends
=========

Mido comes with backends for PortMidi and RtMidi, and an incomplete
one for Pygame. The default is PortMidi.

For more on writing backends, see :doc:`new_port_types`.

(Todo: loaded on demand.)

You can choose backend by setting the ``MIDO_BACKEND`` environment
variable::

    $ MIDO_BACKEND=.rtmidi python program.py

Alternatively, you can set the backend from your program::

    >>> mido.set_backend('.rtmidi')
    >>> mido.backend
    <backend mido.backends.rtmidi (not loaded)>

In either case, the ``mido.open_*()`` and ``mido.get_*()`` will now
use the RtMidi backend.

(The "." in front of the name is a shortcut for ``mido.backends.``, so
the full name is ``mido.backends.rtmidi``.)

You can use multiple backends at the same time. For example, to send
messages from an RtMidi port to a PortMidi port::

    rtmidi = mido.Backend('.rtmidi')
    portmidi = mido.Backend('.portmidi')

    input = rtmidi.open_input()
    output = portmidi.open_output()
    for message in input:
        output.send(message)

By default, ``mido.Backend`` will load the module immediately. If you
want the module loaded on demand you can pass ``load=False``. (This is
what Mido does when it starts up, so the intial backend is not loaded
until you actually use it.)

If you want the ``Backend`` object to respect environment variables
like ``MIDO_DEFAULT_INPUT`` you can pass ``use_environ=True``.


Callbacks
----------

Input ports take a callback argument::

    def func(message):
        print('Callback got{}'.format(message))

    input = mido.open_input(callback=func)

The callback function will be called with every message that arrives
on the port. You can not use the normal methods like ``receive()`` and
``pending()`` when the port has a callback. There is currently no way
to remove or replace the callback.

Callbacks are currently available in PortMidi and RtMidi.


Environment Variables
----------------------

You can override the backend's choice of default ports with these
three environment variables::

    MIDO_DEFAULT_INPUT
    MIDO_DEFAULT_OUTPUT
    MIDO_DEFAULT_IOPORT

For example::

    $ MIDO_DEFAULT_INPUT='SH-201' python program.py

or::

    $ export MIDO_DEFAULT_OUTPUT='SH-201'
    $ python program1.py
    $ python program2.py


PortMidi
---------

Name: ``.portmidi``

The PortMidi backend is written with ``ctypes`` and requires only the
shared library file ``portmidi.so`` or ``portmidi.dll``.

Can send but doesn't receive ``active_sensing`` messages.

PortMidi has no callback mechanism, so callbacks are implemented in
Python with threads. Each port with a callback has a dedicated thread
which does blocking reads from the device.

PortMidi doesn't update its list of ports

In Linux, the list of port names remains fixed after the library has
loaded. (Todo: is this true on other platforms?)


RtMidi
-------

Name: ``.rtmidi``

The RtMidi backend is a thin wrapper around `python-rtmidi
<https://pypi.python.org/pypi/python-rtmidi/>`_

Sends and receives all 18 message types.

Callbacks use RtMidi's own mechanism.

RtMidi is the only backend that can create virtual ports::

    >>> port = mido.open_input('New Port', virtual=True)
    >>> port
    <open input 'New Port' (RtMidi/LINUX_ALSA)>

Other applications can now connect to this port. (One oddity is that,
at least in Linux, RtMidi can't see its own virtual ports, while
PortMidi can see the.)

THE RtMidi library can be compiled with support for more than one
API. You can select API by adding it after the module name, either in
the environment variable::

    $ export MIDO_BACKEND=.rmidi/LINUX_ALSA
    $ export MIDO_BACKEND=.rmidi/LINUX_JACK

or in one of these::

    >>> mido.set_backend('.rtmidi/LINUX_ALSA')
    >>> mido.backend
    <backend mido.backends.rtmidi/LINUX_ALSA (not loaded)>

    >>> mido.Backend('.rtmidi/LINUX_JACK')
    <backend mido.backends.rtmidi/LINUX_JACK (not loaded)>

This allows you to, for example, use both ALSA and JACK ports in the
same program.

To get a list of available APIs::

    >>> mido.backend.module.get_api_names()
    ['LINUX_ALSA', 'UNIX_JACK']

There are a couple of problems with port names in Linux. First, RtMidi
can't see some software ports such as ``amSynth MIDI IN``. PortMidi
uses the same ALSA sequencer API, so this is problem in RtMidi.

Second, ports are named inconsistently. For example the input port
'Midi Through 14:0' has a corresponding output named 'Midi
Through:0'. Unless this was intended, it is a bug in RtMidi's ALSA
implementation.


Pygame
-------

Name: ``.pygame``

The Pygame backend uses ``pygame.midi`` for I/O.

Can send but not receive ``sysex`` and ``active_sensing``.

Callbacks are currently not implemented.

Pygame.midi is implemented on top of PortMidi.
