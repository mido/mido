Mido - MIDI Objects for Python
===============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

.. code:: python

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

.. code:: python

    >>> with input as mido.open_input('SH-201'):
    ...     for msg in input:
    ...         print(msg)

.. code:: python

    >>> msg = mido.Message('program_change', program=10)
    >>> msg.type
    'program_change'
    >>> msg.channel = 2
    >>> msg2 = msg.copy(program=9)
    <program_change message channel=2, program=9, time=0>

See `<docs/tutorial.rst>`_ for more.


Status
-------

Mido is nearly ready for its first official release. All of the basic
functionality is in place. There will be some tweaking of the API to
make it little bit clearer. Other than that, what remains is to polish
up the documentation and nitpick the code a bit.

I am aiming for a release sometime in July 2013.


License
--------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Requirements
-------------

Mido is written for Python 2.7 and 3.2, and runs on Ubuntu and Mac
OS X. May also run on other systems.

If you want to use message ports, you will need `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system. The PortMidi library is loaded on demand, so you can use the parser and messages without it.


Installing
-----------

In the Linux / OS X terminal::

    $ sudo python setup.py install

or::

    $ sudo python3 setup.py install

The PortMidi wrapper is written with `ctypes`, so no compilation is
required.


Installing PortMidi
--------------------

In Ubuntu::

    $ sudo apt-get install libportmidi-dev

I installed it on OS X in `MacPorts <http://www.macports.org/>`_ with::

    $ sudo port install portmidi

It's available in `Homebrew <http://mxcl.github.io/homebrew/>`_ under
the same name.


Future Plans
-------------

* support more MIDI libraries, either distibuted with Mido or as
  separate packages. (A wrapper for `python-rtmidi
  <http://pypi.python.org/pypi/python-rtmidi/>`_ is almost complete.)
  It is unclear how or even if new backends will be integrated with
  Mido, but in the meantime they can be used by calling
  `rtmido.Input()`, `alsamido.Input()` etc.

* add a library of useful tools, such as delays, an event engine and
  message filters.

* support `running status
  <http://www.blitter.com/~russtopia/MIDI/~jglatt/tech/midispec/run.htm>`_
  (This is currently tricky or impossible with PortMidi, but could be
  useful for other data sources.)

* support time codes (0xf1). (These have one data bytes divided into 3
  bits type and 4 bits values. It's unclear how to handle this.)


Known Bugs
-----------

* on OS X, PortMidi usually hangs for a second or two seconds while
  initializing. (It always succeeds.)

* libportmidi prints out error messages instead of returning err and
  setting the error message string. Thus, Mido can't catch errors and
  raise the proper exception. (This can be seen if you try to open a
  port with a given name twice.)

* there is an obscure bug involving the OS X application Midi Keys.
  See tmp/segfault.py.

Latest version of the code: http://github.com/olemb/mido/ .

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/
