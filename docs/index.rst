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

Mido is short for MIDi Objects.


Source code
-----------

Latest stable release: http://github.com/olemb/mido/

Latest development version: http://github.com/olemb/mido/tree/develop/


About This Document
-------------------

This document is available at http://mido.readthedocs.org/

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
