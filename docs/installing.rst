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
<http://portmedia.sourceforge.net/portmidi/>`_,
`python-rtmidi <http://github.com/superquadratic/rtmidi-python>`_
and `Pygame <http://www.pygame.org/docs/ref/midi.html>`_.


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


Installing python-rtmidi
-------------------------

::

    $ pip install python-rtmidi

That may fail in OS X due to a problem with the package. If this
happens, you can try::

   $ pip install --pre python-rtmidi

The ``--pre`` is because pip refuses to install when the library looks
like a pre-release, and says: "Could not find a version that satisfies
the requirement XYZ.")
