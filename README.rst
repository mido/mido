Mido - MIDI Objects for Python
==============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible:

.. code-block:: python

   >>> from mido import Message

   >>> msg = Message('note_on', note=60)
   >>> msg
   <message note_on channel=0 note=60 velocity=64 time=0>

   >>> msg.copy(note=120, time=10)
   <message note_on channel=0 note=120 velocity=64 time=10>

   >>> msg.bytes()
   [144, 60, 64]

   >>> Message.from_bytes([144, 60, 64], time=10)
   <message note_on channel=0 note=60 velocity=64 time=10>

.. code-block:: python

    >>> import mido

    >>> out = mido.open_output()
    >>> out.send(msg)

.. code-block:: python

    >>> for msg in mido.open_input('SH-201'):
    ...     print(msg)

.. code-block:: python

    >>> from mido import MidiFile

    >>> for msg in MidiFile('song.mid').play():
    ...     output.send(msg)

Full documentation at https://mido.readthedocs.io/


Main Features
-------------

* works in Python 2 and 3.

* convenient message objects.

* supports PortMidi, RtMidi and Pygame. New backends are easy to
  write.

* full support for all 18 messages defined by the MIDI standard.

* standard port API allows all kinds of input and output ports to be
  used interchangeably. New port types can be written by subclassing
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

1.2 is the third stable release.

See docs/changes.rst for a full list of changes.


Requirements
------------

Mido targets Python 2.7 and 3.2.

See docs/installing.rst for more on requirements for port backends.


Installing
----------

See docs/installing.rst.


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
  port that has a callback, and in Pygame when you close any port.


Source Code
-----------

Latest version of the code: https://github.com/olemb/mido/ .

Latest development version: https://github.com/olemb/mido/tree/develop/


License
-------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Contact
-------

Ole Martin Bjorndalen - ombdalen@gmail.com
