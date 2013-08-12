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
    <message program_change channel=2, program=9, time=0>

Full documentation at http://mido.readthedocs.org/


Status
-------

This is the first stable release. All basic functionality is in place.
(Messages, ports and parser.)


Requirements
-------------

Mido targets Python 2.7 and 3.2 and runs on Ubuntu and Mac OS X. May
also run on other systems.

If you want to use message ports, you will need `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system. The PortMidi library is loaded on demand, so you can use
the parser and messages without it.


Installing
-----------

To install::

    $ pip install mido

The PortMidi wrapper is written with `ctypes`, so no compilation is
required.

If you want to use ports, you need the PortMidi shared library. The
Ubuntu package is called ``libportmidi-dev``.  PortMidi is also
available in `MacPorts <http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ under the name ``portmidi``.


Documentation
--------------

Documentation is available at http://mido.readthedocs.org/


Known Bugs
-----------

* on OS X, PortMidi usually hangs for a second or two seconds while
  initializing. (It always succeeds.)

* libportmidi prints out error messages instead of returning err and
  setting the error message string. Thus, Mido can't catch errors and
  raise the proper exception. (I've been able to work around this when
  opening ports, so don't know if this is still a problem.)

* there is an obscure bug involving the OS X application Midi Keys.
  See tmp/segfault.py.


Future Plans
-------------

* add a library of useful tools, such as delays, an event engine and
  message filters.

* support `running status
  <http://www.blitter.com/~russtopia/MIDI/~jglatt/tech/midispec/run.htm>`_
  (This is currently tricky or impossible with PortMidi, but could be
  useful for other data sources.)

* support time codes (0xf1). (These have one data bytes divided into 3
  bits type and 4 bits values. It's unclear how to handle this.)


License
--------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Source Code
------------

Latest version of the code: http://github.com/olemb/mido/ .

Latest development version: http://github.com/olemb/mido/tree/develop/


Author
-------

Ole Martin Bjørndalen - ombdalen@gmail.com
