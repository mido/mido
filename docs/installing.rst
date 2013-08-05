Installing Mido
================

Requirements
-------------

Mido targets Python 2.7 and 3.2 and runs on Ubuntu and Mac OS X. May
also run on other systems.

All backends are implemented in Python, so no compilation is
required. The backends are loaded on demand, so there are no external
dependencies unless they are used.

Mido currently supports three different backends: `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_,
`python-rtmidi <http://pypi.python.org/pypi/python-rtmidi/>`_
and `pygame <http://www.pygame.org/docs/ref/midi.html>`_.


Installing
-----------

To install::

    $ pip install mido

PortMidi is available in Ubuntu as ``libportmidi-dev`` and in
`MacPorts <http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ as ``portmidi``.

python-rtmidi can be installed with:

    $ pip install python-rtmidi

It requires ``librtmidi.so``, which is available in Ubuntu as
``librtmidi-dev``.
