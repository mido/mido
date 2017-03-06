RtMidi (Default, Recommended)
-----------------------------

Name: ``mido.backends.rtmidi``

The RtMidi backend is a thin wrapper around `python-rtmidi
<https://pypi.python.org/pypi/python-rtmidi/>`_


Features:

* callbacks

* true blocking ``receive()`` in Python 3 (using a callback and a
  queue)

* virtual ports

* ports can be opened multiple times, each will receive a copy of each message

* client name can be specified when opening a virtual port

* sends but doesn't receive active sensing

* port list is always up to date

* all methods but ``close()`` are thread safe


Port Names (Linux/ALSA
^^^^^^^^^^^^^^^^^^^^^^

When you're using Linux/ALSA the port names include client name and
ALSA client and port numbers, for example:

.. code-block:: python

    >>> mido.get_output_names()
    ['TiMidity:TiMidity port 0 128:0']

The ALSA client and port numbers ("128:0" in this case) can change
from session to session, making it hard to hard code port names or use
them in config files.

To get around this the RtMidi backend allows you to leave out the the
port number of port number and client names. These lines will all open
the port above:

.. code-block:: python

    mido.open_output('TiMidity port 0')

.. code-block:: python

    mido.open_output('TiMidity:TiMidity port 0')

.. code-block:: python

    mido.open_output('TiMidity:TiMidity port 0 128:0')

There is currently no way to list ports without port number or client
name. This can be added in a future version of there is demand for it
and a suitable API is found.


Virtual Ports
^^^^^^^^^^^^^

RtMidi is the only backend that can create virtual ports:

.. code-block:: python

    >>> port = mido.open_input('New Port', virtual=True)
    >>> port
    <open input 'New Port' (RtMidi/LINUX_ALSA)>

Other applications can now connect to this port. (One oddity is that,
at least in Linux, RtMidi can't see its own virtual ports, while
PortMidi can see them.)


Client Name
^^^^^^^^^^^

You can specify a client name for the port:  (New in 1.2.0.)

.. code-block:: python

    >>> port = mido.open_input('New Port', client_name='My Client')

This requires python-rtmidi >= 1.0rc1. If ``client_name`` is passed
the port will be a virtal port.

.. note:: Unfortunately, at least with ALSA, opening two ports with
          the same ``client_name`` creates two clients with the same
          name instead of one client with two ports.

There are a couple of problems with port names in Linux. First, RtMidi
can't see some software ports such as ``amSynth MIDI IN``. PortMidi
uses the same ALSA sequencer API, so this is problem in RtMidi.

Second, in some versions of RtMidi ports are named inconsistently. For
example, the input port 'Midi Through 14:0' has a corresponding output
named 'Midi Through:0'. Unless this was intended, it is a bug in
RtMidi's ALSA implementation.


Choosing API
^^^^^^^^^^^^

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
