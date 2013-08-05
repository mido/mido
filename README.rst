Mido - MIDI Objects for Python
===============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible:

.. code-block:: pycon

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

.. code-block:: pycon

    >>> with input as mido.open_input('SH-201'):
    ...     for msg in input:
    ...         print(msg)

.. code-block:: pycon

    >>> msg = mido.Message('program_change', program=10)
    >>> msg.type
    'program_change'
    >>> msg.channel = 2
    >>> msg2 = msg.copy(program=9)
    <program_change message channel=2, program=9, time=0>

Full documentation at http://mido.readthedocs.org/


Main Features
--------------

  * convenient message objects.

  * standard port API allows all kinds of input and output ports to be
    used interchangingly. New port types can be written by subclassing
    and overriding a few methods, or by duck typing.

  * supports PortMidi, rtmidi and pygame. New backends can be written
    easily and used with Mido.

  * full support for MIDI files (read, write, create and play) with
    complete access to every message in the file.

  * allows MIDI over TCP/IP with socket ports.

  * reusable MIDI parser.

  * works in Python 2 and 3.


Status
-------

1.1 is the second stable release.

1.0 established the basic functionality (messages, ports and parser),
while 1.1 adds MIDI files, MIDI over TCP/IP (socket ports) and many
improvements to the port API (including reset() and panic() methods
for output ports.)


Requirements
-------------

Mido targets Python 2.7 and 3.2.

If you want to use message ports, you will need `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system. The PortMidi library is loaded on demand, so you can use
the parser and messages without it.

The PortMidi wrapper is tested on on Ubuntu and Mac OS X, but may also
run on other systems where the ``portmidi.so/dll`` file is available.

Alternative backends are included for `python-rtmidi
<http://pypi.python.org/pypi/python-rtmidi/>`_ and `pygame
<http://www.pygame.org/docs/ref/midi.html>`_. These can be selected
with an environment variable::

    export MIDO_BACKEND=mido.backends.pygame
    python some_program.py

Like PortMidi, these are loaded on demand.


Installing
-----------

To install::

    $ pip install mido

The PortMidi wrapper is written with `ctypes`, so no compilation is
required.

If you want to use ports, you need the PortMidi shared library. The
Ubuntu package is called ``libportmidi-dev``, while the `MacPorts
<http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ packages are called ``portmidi``.


Documentation
--------------

Documentation is available at http://mido.readthedocs.org/


Source code
------------

Latest stable release: http://github.com/olemb/mido/

Development version: http://github.com/olemb/mido/tree/develop/


Known Bugs
-----------

* on OS X, PortMidi usually hangs for a second or two seconds while
  initializing. (It always succeeds.)

* (this is no longer a problem:) libportmidi prints out error messages
  instead of returning err and setting the error message string. Thus,
  Mido can't catch errors and raise the proper exception. I've been
  able to work around this when opening ports, which is the only place
  where this was a problem, as far as I know.

* there is an obscure bug involving the OS X application Midi Keys.
  See tmp/segfault.py.


Future Plans
-------------

* implement saving of MIDI meta messages

* add a library of useful tools, such as delays, an event engine and
  message filters.


License
--------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Author
-------

Ole Martin Bjørndalen - ombdalen@gmail.com
