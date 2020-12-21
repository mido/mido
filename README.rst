Mido - MIDI Objects for Python
==============================

.. image:: https://github.com/mido/mido/workflows/Test/badge.svg
   :target: https://github.com/mido/mido/actions

Mido is a library for working with MIDI messages and ports:

.. code-block:: python

   >>> import mido
   >>> msg = mido.Message('note_on', note=60)
   >>> msg.type
   'note_on'
   >>> msg.note
   60
   >>> msg.bytes()
   [144, 60, 64]
   >>> msg.copy(channel=2)
   Message('note_on', channel=2, note=60, velocity=64, time=0)

.. code-block:: python

   port = mido.open_output('Port Name')
   port.send(msg)

.. code-block:: python

    with mido.open_input() as inport:
        for msg in inport:
            print(msg)

.. code-block:: python

    mid = mido.MidiFile('song.mid')
    for msg in mid.play():
        port.send(msg)


Full documentation at https://mido.readthedocs.io/


Main Features
-------------

* works in Python 2 and 3.

* convenient message objects.

* supports RtMidi, PortMidi and Pygame. New backends are easy to
  write.

* full support for all 18 messages defined by the MIDI standard.

* standard port API allows all kinds of input and output ports to be
  used interchangeably. New port types can be written by subclassing
  and overriding a few methods.

* includes a reusable MIDI stream parser.

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


Requirements
------------

Mido targets Python 3.6 and 2.7.


Installing
----------

::

    pip install mido

If you want to use ports::

   pip install python-rtmidi

See ``docs/backends/`` for other backends.



Source Code
-----------

https://github.com/mido/mido/


License
-------

Mido is released under the terms of the `MIT license
<http://en.wikipedia.org/wiki/MIT_License>`_.


Questions and suggestions
-------------------------

For questions and proposals which may not fit into issues or pull requests, we
recommend to ask and discuss on `Discussions
<https://github.com/mido/mido/discussions>`_.
