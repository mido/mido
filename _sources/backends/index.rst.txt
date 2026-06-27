.. SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Backends
========

A backend provides the interface between Mido and the operating system level
MIDI stack.

Some Mido features are only available with select backends.

Mido's backend subsystem has been designed to be extensible so you can add
your own backends if required. See :doc:`custom`.

Providing platform specific Python-native backends is currently evaluated.
See: https://github.com/mido/mido/issues/506

.. todo:: Insert a stack diagram to clear things up.


Choice
------

Mido comes with five backends:

* :doc:`RtMidi <rtmidi>` is the *default* and *recommended* backend. It has all
  the features of the other ones and more plus it is usually easier to install.

* :doc:`PortMidi <portmidi>` was the default backend up until version 1.2. It
  uses the ``portmidi`` shared library and can be difficult to install on some
  systems.

* :doc:`Pygame <pygame>` uses the ``pygame.midi`` module.

* :doc:`rtmidi-python <rtmidi_python>` uses the ``rtmidi_python`` package, an
  alternative wrapper for PortMidi. It is currently very basic but
  easier to install on some Windows systems.

* :doc:`Amidi <amidi>` is an experimental backend for Linux/ALSA
  that uses the command ``amidi`` to send and receive messages.

You can set the backend using an environment variable: See :ref:`env_vars`.

Alternatively, you can set the backend from within your program::

    >>> mido.set_backend('mido.backends.portmidi')
    >>> mido.backend
    <backend mido.backends.portmidi (not loaded)>

.. note::

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

If you pass ``use_environ=True``, the module will use the environment
variables ``MIDO_DEFAULT_INPUT`` etc. for default ports.


.. _env_vars:

Environment Variables
---------------------


Select Backend
^^^^^^^^^^^^^^

If you want to use a backend other than RtMidi you can override this with
the ``MIDO_BACKEND`` environment variable, for example::

    $ MIDO_BACKEND=mido.backends.portmidi ./program.py


Set Default ports
^^^^^^^^^^^^^^^^^

You can override the backend's choice of default ports with these
three environment variables::

    MIDO_DEFAULT_INPUT
    MIDO_DEFAULT_OUTPUT
    MIDO_DEFAULT_IOPORT

For example::

    $ MIDO_DEFAULT_INPUT='SH-201' python3 program.py

or::

    $ export MIDO_DEFAULT_OUTPUT='Integra-7'
    $ python3 program1.py
    $ python3 program2.py


Available Backends
------------------

.. toctree::

   rtmidi
   portmidi
   pygame
   rtmidi_python
   amidi

.. include:: custom.rst
