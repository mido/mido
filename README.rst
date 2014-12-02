Mido - MIDI Objects for Python
==============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible:

.. code-block:: python

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

.. code-block:: python

    >>> with input as mido.open_input('SH-201'):
    ...     for message in input:
    ...         print(message)

.. code-block:: python

    >>> message = mido.Message('program_change', program=10)
    >>> message.type
    'program_change'
    >>> message.channel = 2
    >>> message.copy(program=9)
    <message program_change channel=2 program=9 time=0>

.. code-block:: python

    >>> from mido import MidiFile
    >>> for message in MidiFile('song.mid').play():
    ...     output.send(message)

Full documentation at http://mido.readthedocs.org/


Main Features
-------------

* works in Python 2 and 3.

* convenient message objects.

* supports PortMidi, RtMidi and Pygame. New backends are easy to
  write.

* full support for all 18 messages defined by the MIDI standard.

* standard port API allows all kinds of input and output ports to be
  used interchangingly. New port types can be written by subclassing
  and overriding a few methods.

* includes a reusable MIDI parser.

* full support for MIDI files (read, write, create and play) with
  complete access to every message in the file, including all common
  meta messages.

* can read and write SYX files (binary and plain text).

* implements (somewhat experimental) MIDI over TCP/IP with socket
  ports. This allows for example wireless MIDI between two
  computers.

* includes programs for playing MIDI files, listing ports and
  serving and forwarding ports over a network.


Status
------

1.1 is the second stable release.

See docs/changes.rst for a full list of changes.


Requirements
------------

Mido targets Python 2.7 and 3.2.

If you want to use message ports, you will need `PortMidi
<http://portmedia.sourceforge.net/portmidi/>`_ installed on your
system. The PortMidi library is loaded on demand, so you can use the
parser and messages without it.

The PortMidi wrapper is tested on on Ubuntu and Mac OS X, but may also
run on other systems where the ``portmidi.so/dll`` file is available.

Alternative backends are included for `python-rtmidi
<http://pypi.python.org/pypi/python-rtmidi/>`_ and `Pygame
<http://www.pygame.org/docs/ref/midi.html>`_. These can be selected
with the environment variable ``MIDO_BACKEND`` or by calling
``mido.set_backend()``.

Like PortMidi, these are loaded on demand.


Installing
----------

To install::

    $ pip install mido

The PortMidi wrapper is written with `ctypes`, so no compilation is
required.

If you want to use ports, you need the PortMidi shared library. The
Ubuntu package is called ``libportmidi-dev``, while the `MacPorts
<http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ packages are called ``portmidi``.

To build documentation locally::

    python setup.py docs

This requires Sphinx. The resulting files can be found in
``docs/_build/``.


Known Bugs
----------

* in OS X, PortMidi and RtMidi usually hang for a second or two
  seconds while initializing. This is actually not a Mido bug, but
  something that happens at a lower level.

* PortMidi in Ubuntu is mistakenly compiled in debug mode, which causes it
  to print out error message instead of returning an error code::

    PortMidi: `Bad pointer'
    type ENTER...PortMidi call failed...

  See https://bugs.launchpad.net/ubuntu/+source/portmidi/+bug/890600

  This means here is no way for Mido to catch the error and raise an
  exception.

  This regularity occurs in two places: in PortMidi when you close a
  port that has a callback, and in pygame when you close any port.


Source Code
-----------

Latest version of the code: http://github.com/olemb/mido/ .

Latest development version: http://github.com/olemb/mido/tree/develop/


License
-------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Contact
-------

Ole Martin Bjorndalen - ombdalen@gmail.com
