.. SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

amidi (Experimental)
--------------------

Name: ``mido.backends.amidi``

Resources:

* `The Advanced Linux Sound Architecture (ALSA) project
  <https://www.alsa-project.org/>`_

* `ALSA Opensrc Org amidi <https://alsa.opensrc.org/Amidi>`_

Features
^^^^^^^^

* Linux only.

* very basic implementation.

* no callbacks

* can only access physical ports. (Devices that are plugged-in.)

* high overhead when sending since it runs a new ``amidi`` command for
  each message.

* known bug: is one behind when receiving messages. See below.


Operation
^^^^^^^^^

The ``amidi`` command (part of ALSA and the `alsa-utils` package) is used for
I/O:

* ``amidi -l`` to list messages (in ``get_input_names()`` etc.)

* ``amidi -d -p DEVICE`` to receive messages. ``amidi`` prints these
  out one on each line as hex bytes. Unfortunately it puts the newline
  at the beginning of the line which flushes the buffer before the
  message instead of after. This causes problems with non-blocking
  receiption using ``select.poll()`` which means messages are received
  one behind. This needs to be looked into.

* ``amidi --send-hex MESSAGE_IN_HEX -p DEVICE`` to send
  messages. Since this is called for every message the overhead is
  very high.
