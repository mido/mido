.. Mido documentation master file, created by
   sphinx-quickstart on Wed Jun 26 16:58:08 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Mido - MIDI Objects for Python
===============================

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible. A quick
example::

    >>> import mido
    >>> output = mido.open_output()
    >>> output.send(mido.Message('note_on', note=60, velocity=64))

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

