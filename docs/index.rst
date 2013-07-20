.. Mido documentation master file, created by
   sphinx-quickstart on Wed Jun 26 16:58:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mido - MIDI Objects for Python
===============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

.. code-block:: pycon

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

.. code-block:: pycon

    >>> with input as mido.open_input('SH-201'):
    ...     for msg in input:
    ...         print(msg)

.. code-block:: pycon

    >>> msg = mido.Message('program_change', program=10)
    >>> msg.type
    'program_change'
    >>> msg.channel = 2
    >>> msg2 = msg.copy(program=9)
    <program_change message channel=2, program=9, time=0>

The latest version of the source code is available at:
http://github.com/olemb/mido/


Community and Contacting the Author:

IRC channel #mido on freenode.net (as olemb)

http://reddit.com/r/midopy/ (as halloi)

ombdalen@gmail.com


Contents:

.. toctree::
   :maxdepth: 2

   why_mido
   tutorial
   lib
   message_types
   parsing_and_encoding
   string_encoding
   new_port_types
   about_midi
   license
   acknowledgements


Indices and tables
==================

* :ref:`genindex`

* :ref:`modindex`

* :ref:`search`

