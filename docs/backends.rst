Backends
========

Choosing Backend
----------------

Mido comes with backends for PortMidi, RtMidi and Pygame.

By default, Mido uses PortMidi. You can override this with the
``MIDO_BACKEND`` environment variable, for example::

    $ MIDO_BACKEND=mido.backends.rtmidi ./program.py

Alternatively, you can set the backend from within your program::

    >>> mido.set_backend('mido.backends.rtmidi')
    >>> mido.backend
    <backend mido.backends.rtmidi (not loaded)>

This will override the environment variable.

If you want to use more than one backend at a time, you can do::

    rtmidi = mido.Backend('mido.backends.rtmidi')
    portmidi = mido.Backend('mido.backends.portmidi')

    input = rtmidi.open_input()
    output = portmidi.open_output()
    for message in input:
        output.send(message)

The backend will not be loaded until you call one of the ``open_`` or
``get_`` methods. You can pass ``load=True`` to have it loaded right
away.

If you pass ``use_environ=True`` the module will use the environment
variables ``MIDO_DEFAULT_INPUT`` etc. for default ports.


Environment Variables
---------------------

You can override the backend's choice of default ports with these
three environment variables::

    MIDO_DEFAULT_INPUT
    MIDO_DEFAULT_OUTPUT
    MIDO_DEFAULT_IOPORT

For example::

    $ MIDO_DEFAULT_INPUT='SH-201' python program.py

or::

    $ export MIDO_DEFAULT_OUTPUT='Integra-7'
    $ python program1.py
    $ python program2.py


PortMidi
--------

Name: ``mido.backends.portmidi``

The PortMidi backend is written with ``ctypes`` and requires only the
shared library file ``portmidi.so`` or ``portmidi.dll``.

Can send but doesn't receive ``active_sensing`` messages.

PortMidi has no callback mechanism, so callbacks are implemented in
Python with threads. Each port with a callback has a dedicated thread
doing blocking reads from the device.

Due to limitations in PortMidi the port list will not be up-to-date if
there are any ports open. (The refresh is implemented by
re-initalizing PortMidi which would break any open ports.)


RtMidi
------

Name: ``mido.backends.rtmidi``

The RtMidi backend is a thin wrapper around `python-rtmidi
<https://pypi.python.org/pypi/python-rtmidi/>`_

Sends but doesn't receive active sensing.

Callbacks use RtMidi's own mechanism.

RtMidi is the only backend that can create virtual ports::

    >>> port = mido.open_input('New Port', virtual=True)
    >>> port
    <open input 'New Port' (RtMidi/LINUX_ALSA)>

Other applications can now connect to this port. (One oddity is that,
at least in Linux, RtMidi can't see its own virtual ports, while
PortMidi can see them.)

The RtMidi library can be compiled with support for more than one
API. You can select API by adding it after the module name, either in
the environment variable::

    $ export MIDO_BACKEND=mido.backends.rtmidi/LINUX_ALSA
    $ export MIDO_BACKEND=mido.backends.rtmidi/UNIX_JACK

or in one of these::

    >>> mido.set_backend('mido.backends.rtmidi/LINUX_ALSA')
    >>> mido.backend
    <backend mido.backends.rtmidi/LINUX_ALSA (not loaded)>

    >>> mido.Backend('mido.backends.rtmidi/UNIX_JACK')
    <backend mido.backends.rtmidi/UNIX_JACK (not loaded)>

This allows you to, for example, use both ALSA and JACK ports in the
same program.

To get a list of available APIs::

    >>> mido.backend.module.get_api_names()
    ['LINUX_ALSA', 'UNIX_JACK']

There are a couple of problems with port names in Linux. First, RtMidi
can't see some software ports such as ``amSynth MIDI IN``. PortMidi
uses the same ALSA sequencer API, so this is problem in RtMidi.

Second, ports are named inconsistently. For example, the input port
'Midi Through 14:0' has a corresponding output named 'Midi
Through:0'. Unless this was intended, it is a bug in RtMidi's ALSA
implementation.


Pygame
------

Name: ``mido.backends.pygame``

The Pygame backend uses ``pygame.midi`` for I/O.

Can send but not receive ``sysex`` and ``active_sensing``.

Callbacks are currently not implemented.

Pygame.midi is implemented on top of PortMidi.
