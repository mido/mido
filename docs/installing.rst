Installing Mido
===============

Requirements
------------

Mido targets Python 2.7 and 3.2. It is developed and tested in Ubuntu
and Mac OS X, but should also work in Windows.

There are no external dependencies unless you want to use the port
backends, which are loaded on demand.

Mido comes with backends for `RtMidi (python-rtmidi)
<http://github.com/superquadratic/rtmidi-python>`_ , `PortMidi
<http://portmedia.sourceforge.net/portmidi/>`_ and `Pygame
<http://www.pygame.org/docs/ref/midi.html>`_. See :doc:`backends/index` for
help choosing a backend.


Installing
----------

To install::

    pip install mido

If you want to use ports::

    pip install python-rtmidi

If that doesn't work this sometimes helps::

    pip install --pre python-rtmidi

See below for instructions on installing other backends.


Installing RtMidi (Default, Recommended)
----------------------------------------

python-rtmidi requires ``librtmidi.so``, which is available in Ubuntu
as ``librtmidi-dev`` (and possible also available as a package in
MacPorts and Homebrew.

Ideally this should work::

    $ pip install python-rtmidi

but the package appears to be broken in PyPI. To get around this you can do::

   $ pip install --pre python-rtmidi

The ``--pre`` is because pip refuses to install when the library looks
like a pre-release, and says: "Could not find a version that satisfies
the requirement XYZ.")


Installing PortMidi
-------------------

PortMidi is available in Ubuntu as ``libportmidi-dev`` and in
`MacPorts <http://www.macports.org/>`_ and `Homebrew
<http://mxcl.github.io/homebrew/>`_ as ``portmidi``.
