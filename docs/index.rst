.. Mido documentation master file, created by
   sphinx-quickstart on Wed Jun 26 16:58:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mido - MIDI Objects for Python
==============================

Version |version|

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

.. code-block:: python

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

.. code-block:: python

    >>> with mido.open_input('SH-201') as inport:
    ...     for msg in inport:
    ...         print(msg)

.. code-block:: python

    >>> from mido import Message
    >>> msg = Message('program_change', program=1)
    >>> msg
    <message program_change channel=0 program=1 time=0>
    >>> msg.copy(program=2, time=100)
    <message program_change channel=0 program=2 time=100>
    >>> msg.time
    100
    >>> msg.bytes()
    [192, 1]

.. code-block:: python

    >>> from mido import MidiFile
    >>> for msg in MidiFile('song.mid').play():
    ...     output.send(msg)


Mido is short for MIDi Objects.


Source code
-----------

https://github.com/olemb/mido/


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
   installing
   contributing
   intro
   messages
   ports
   midi_files
   syx
   backends
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
