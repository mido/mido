Installing Mido
===============

Requirements
------------

Mido targets Python 3.6 and 2.7.

There are no external dependencies unless you want to use the port
backends, which are loaded on demand.

Mido comes with backends for RtMidi
(`python-rtmidi <https://github.com/SpotlightKid/python-rtmidi>`_ or
`rtmidi_python <https://mido.readthedocs.io/en/latest/backends/rtmidi_python.html>`_),
`PortMidi <http://portmedia.sourceforge.net/portmidi/>`_ and
`Pygame <http://www.pygame.org/docs/ref/midi.html>`_. See :doc:`backends/index` for
help choosing a backend.


Installing
----------

To install::

    pip install mido

If you want to use ports::

    pip install python-rtmidi

See :doc:`backends/index` for installation instructions for other
backends.
