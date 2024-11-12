.. SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

Pygame
------

Name: ``mido.backends.pygame``

Resources:

* `PyGame Python Library <https://www.pygame.org>`_
* `PortMidi C Library <https://github.com/PortMidi/portmidi>`_

The Pygame backend uses the `pygame.midi
<https://www.pygame.org/docs/ref/midi.html>`_ module for I/O.

Features
^^^^^^^^

* Doesn't receive ``active_sensing``.

* Callbacks are currently not implemented.

* Pygame.midi is implemented on top of PortMidi.
