Installing Mido
===============

Requirements
------------

Mido targets Python 2.7 and 3.2. It is developed and tested in Ubuntu
and Mac OS X but should also work in Windows.

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

See :doc:`backends/index` for installation instructions for other
backends.
