.. Mido documentation master file, created by
   sphinx-quickstart on Wed Jun 26 16:58:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mido - MIDI Objects for Python
==============================

Version |version|

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible:

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
   <message note_on channel=2 note=60 velocity=64 time=0>

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


Mido is short for MIDI objects.


Source code
-----------

https://github.com/mido/mido/


About This Document
-------------------

This document is available at https://mido.readthedocs.io/

To build locally::

    python setup.py docs

This requires Sphinx. The resulting files can be found in
``docs/_build/``.


Contents
--------

.. toctree::
   :maxdepth: 2

   changes
   roadmap
   installing
   backends/index
   contributing
   intro
   messages
   frozen_messages
   ports
   midi_files
   syx
   parsing
   string_encoding
   socket_ports
   bin
   implementing_ports
   implementing_backends
   freezing
   about_midi
   message_types
   meta_message_types
   lib
   resources
   license
   authors
   acknowledgements




Indices and tables
------------------

* :ref:`genindex`

* :ref:`modindex`

* :ref:`search`
