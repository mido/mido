Mido - MIDI Objects for Python
===============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

.. code:: python

    >>> import mido
    >>> m = mido.new('note_on', note=60, velocity=100)

.. code:: python

    >>> m.type
    'note_on'
    >>> m.channel = 2
    >>> m.copy(note=62, velocity=73)
    <note_on message channel=2, note=62, velocity=73, time=0>

Messages can be sent and received on ports:

.. code:: python

    input = mido.input()  # Default input
    output = mido.output('SH-201')

    for message in input:
        output.send(message)

Blocking and nonblocking receive are supported, as well as blocking
and non-blocking receive from multiple ports. Ports can be used with
the `with` statement, and input ports can be iterated over in both a
blocking and non-blocking way.

See `<docs/tutorial.rst>`_ for more.


Features
---------

* Full implementation of all standard MIDI messages.

* Full name, type and value checking of keyword arguments
  and attributes ensures that you always have a valid message.

* Sysex is supported, with data bytes as a tuple of integers.

* Support for Python 2 and 3.

* Can easily be integrated with other libraries and tools. (Messages
  can be encoded to and decoded from many formats, including lists of
  bytes, bytearrays, hex strings and text strings.)

* Includes a flexible MIDI parser which can be used to parse MIDI from
  any source or format by feeding it bytes and fetching the produced
  messages.)

* Custom port types and wrappers for other MIDI libraries can be
  written and used with Mido by implementing the simple port
  API. (Uses duck typing.)

* Text serialization format for messages. (Can be safely embedded in
  most text file formats and protocols without escaping.)

* Fully documented, with tutorial.

* Includes a fairly complete unit test suite. (Ports are not tested
  yet.)


Status
-------

Mido is nearly ready for its first official release. All of the basic
functionality is in place, and the API is unlikely to change from this
point. What remains is mostly to polish up the documentation and
nitpick the code a bit.

I am aiming for a release sometime in July 2013.


License
--------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Requirements
-------------

Requires Python 2.7 or 3.2. Runs on Ubuntu and Mac OS X. May also run
on other systems.

If you want to use message ports, you will need `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system. Mido loads `libportmidi.so` / `.dll` on demand when you
open a port or call one of the I/O functions like
`mido.input_names()`. The wrapper module is written with ctypes and
requires no compilation.


Installing
-----------

In the Linux / OS X terminal::

    $ sudo python setup.py install

or::

    $ sudo python3 setup.py install


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
  `rtmido.input()`, `alsamido.input()` etc.

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


More About MIDI
----------------

http://www.midi.org/

Mido is short for MIDi Objects (or Musical Instrument Digital
Objects). It is pronounced with i and in "little" and o as in
"object", or in Japanese: ミド.

Latest version of the code: http://github.com/olemb/mido/ .

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

The PortMidi wrapper is based on portmidizero by Grant Yoshida.

Thanks to tialpoy on Reddit for extensive code review and helpful
suggestions.
