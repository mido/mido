Backends
========

.. toctree::
   :maxdepth: 1

   rtmidi
   portmidi
   pygame
   rtmidi_python
   amidi


Choosing a Backend
------------------

Mido comes with five backends:

* :doc:`RtMidi <rtmidi>` is the recommended backends. It has all the
  features of the other ones and more and is usually easier to
  install.

* :doc:`PortMidi <portmidi>` was the default backend up until 1.2. It
  uses the ``portmidi`` shared library and can be difficult to install
  on some systems.

* :doc:`Pygame <pygame>` uses the ``pygame.midi``.

* :doc:`rtmidi-python <rtmidi_python>` uses the ``rtmidi_python`` package, an
  alternative wrapper for PortMidi. It is currently very basic but
  easier to install on some Windows systems.

* :doc:`Amidi <amidi>` is an experimental backend for Linux/ALSA
  that uses the command ``amidi`` to send and receive messages.

If you want to use another than the RtMidi you can override this with
the ``MIDO_BACKEND`` environment variable, for example::

    $ MIDO_BACKEND=mido.backends.portmidi ./program.py

Alternatively, you can set the backend from within your program::

    >>> mido.set_backend('mido.backends.portmidi')
    >>> mido.backend
    <backend mido.backends.portmidi (not loaded)>

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
