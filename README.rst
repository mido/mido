.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Mido - MIDI Objects for Python
==============================

.. image:: https://img.shields.io/badge/License-MIT-blue.svg
   :alt: MIT License
   :target: https://github.com/mido/mido/blob/main/LICENSES/MIT.txt

.. image:: https://img.shields.io/pypi/v/mido.svg
   :alt: PyPi version
   :target: https://pypi.org/project/mido

.. image:: https://img.shields.io/pypi/pyversions/mido.svg
   :alt: Python version
   :target: https://python.org

.. image:: https://pepy.tech/badge/mido
   :alt: Downloads
   :target: https://pepy.tech/project/mido

.. image:: https://github.com/mido/mido/actions/workflows/test.yml/badge.svg
   :alt: Test status
   :target: https://github.com/mido/mido/actions/workflows/test.yml

.. image:: https://readthedocs.org/projects/mido/badge/?version=latest
   :alt: Docs status
   :target: https://mido.readthedocs.io/

.. image:: https://api.reuse.software/badge/github.com/mido/mido
   :alt: REUSE status
   :target: https://api.reuse.software/info/github.com/mido/mido

.. image:: https://www.bestpractices.dev/projects/7987/badge
   :alt: OpenSSF Best Practices
   :target: https://www.bestpractices.dev/projects/7987

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

1.3 is the fourth stable release.

This project uses `Semantic Versioning <https://semver.org>`_.


Requirements
------------

Mido requires Python 3.7 or higher.


Installing
----------

::

    python3 -m pip install mido

Or, alternatively, if you want to use ports with the default backend::

   python3 -m pip install mido[ports-rtmidi]

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

For questions and proposals which may not fit into issues or pull requests,
we recommend to ask and discuss in the `Discussions
<https://github.com/mido/mido/discussions>`_ section.
