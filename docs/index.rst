.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
.. SPDX-FileCopyrightText: 2023 Raphaël Doursenaud <rdoursenaud@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

.. Mido documentation main file, created by
   sphinx-quickstart on Wed Jun 26 16:58:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. include:: shared/licenses_logos.rst


Mido - MIDI Objects for Python
==============================


.. Main TOC to get a proper title in the PDF:
.. toctree::
   :caption: Table of Contents
   :maxdepth: 4


.. Workaround to properly show parts in both PDF (latex) and HTML (ReadTheDocs)
   While awaiting a resolution of
   https://github.com/sphinx-doc/sphinx/issues/4977
.. raw:: latex

   \part{Introduction}

.. toctree::
   :caption: Introduction
   :maxdepth: 3
   :hidden:

   self


Overview
--------

Mido is a :term:`Python` library for working with
:term:`MIDI` 1.0 :term:`ports`, :term:`messages` and :term:`files`:

.. code-block:: python

 from mido import MidiFile, MidiTrack, Message

# Create a new MIDI file
mid = MidiFile()
track = MidiTrack()
mid.tracks.append(track)

# Set tempo (120 BPM)
track.append(Message('program_change', program=0, time=0))

# Generate a simple piano rap melody
# Notes are in MIDI format (60 = Middle C), with time in ticks
melody = [
    (60, 480), (62, 240), (64, 240), # Phrase 1: C-D-E (quarter note + two eighth notes)
    (65, 480), (64, 240), (62, 240), # Phrase 2: F-E-D (quarter note + two eighth notes)
    (60, 960),                      # Phrase 3: C (half note)
    (67, 480), (65, 240), (64, 240), # Phrase 4: G-F-E (quarter note + two eighth notes)
    (62, 480), (60, 480)            # Phrase 5: D-C (two quarter notes)
]

# Add notes to the MIDI track
for note, duration in melody:
    track.append(Message('note_on', note=note, velocity=64, time=0))  # Note on
    track.append(Message('note_off', note=note, velocity=64, time=duration))  # Note off

# Save the file
file_path = '/mnt/data/Piano_Rap_Melody.mid'
mid.save(file_path)
file_path


Mido is short for *MIDI objects*.


About this document
^^^^^^^^^^^^^^^^^^^

.. version is automatically generated.

This document refers to Mido version |release|.

.. note::

   An up-to-date version of this document is always available at
   https://mido.readthedocs.io.

.. Build instructions have been moved to contributing.


License
^^^^^^^

This documentation (Except our code of conduct) is licensed under the
`Creative Commons Attribution 4.0 International
License <https://creativecommons.org/licenses/by/4.0/>`__.

|Creative Commons BY-4.0 License|

.. seealso::

   :doc:`licenses`


Community & Source Code
^^^^^^^^^^^^^^^^^^^^^^^

Come visit us at https://github.com/mido.

Everybody is welcome!

.. seealso::

   * :doc:`CODE_OF_CONDUCT`

   * :doc:`contributing`


.. Indices are systematically generated for the PDF.
   Wrap into an HTML only section to prevent spurious title in the TOC.
.. only:: html

    Tables and indices
    ------------------

    * :ref:`genindex`

    * :ref:`modindex`

    .. Comment since Search is provided by the ReadTheDocs theme.
    .. * :ref:`search`


.. The rest of the TOC and documents:

.. raw:: latex

   \part{Basics}

.. toctree::
   :caption: Basics
   :maxdepth: 3
   :hidden:

   installing
   intro


.. raw:: latex

   \part{Details}

.. toctree::
   :caption: Details
   :maxdepth: 3
   :hidden:

   messages/index
   backends/index
   ports/index
   files/index
   binaries


.. raw:: latex

   \part{Reference}

.. toctree::
   :caption: Reference
   :maxdepth: 3
   :hidden:

   api


.. raw:: latex

   \part{Community}

.. toctree::
   :caption: Community
   :maxdepth: 3
   :hidden:

   CODE_OF_CONDUCT
   contributing


.. raw:: latex

   \part{Appendix}

.. toctree::
   :caption: Appendix
   :maxdepth: 3
   :hidden:

   about_midi
   message_types
   meta_message_types
   resources

   freezing_exe

   changes

   authors
   licenses
   acknowledgements

   glossary
