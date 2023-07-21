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


Overview
--------

Mido is a :term:`Python` library for working with
:term:`MIDI` 1.0 :term:`ports`, :term:`messages` and :term:`files`:

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


Mido is short for *MIDI objects*.


About this document
^^^^^^^^^^^^^^^^^^^

This document refers to Mido version |version|.

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

   * :doc:`code_of_conduct`

   * :doc:`contributing`


Basics
------

.. toctree::
   :maxdepth: 3

   installing
   intro


Details
-------

.. toctree::
   :maxdepth: 3

   messages/index
   backends/index
   ports/index
   files/index
   binaries


Reference
---------

.. toctree::
   :maxdepth: 3

   api


Community
---------

.. toctree::
   :maxdepth: 3

   code_of_conduct
   contributing


Appendix
--------

.. toctree::
   :maxdepth: 3

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

Indices and tables
------------------

* :ref:`genindex`

* :ref:`modindex`

* :ref:`search`
