.. SPDX-FileCopyrightText: 2017 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

PortMidi
--------

Name: ``mido.backends.portmidi``

Resources:

* `PortMidi C Library <https://github.com/PortMidi/portmidi>`_


Installing
^^^^^^^^^^

The PortMidi backend requires the ``portmidi`` shared library.

`Ubuntu <https://www.ubuntu.com/>`_::

    apt install libportmidi-dev

`Homebrew <https://mxcl.dev/homebrew/>`_::

    brew install portmidi

`MacPorts <https://www.macports.org/>`_::

    port install portmidi

The backend will look for::

    portmidi.so      (Linux)
    portmidi.dynlib  (macOS)
    portmidi.dll     (Windows)


Features
^^^^^^^^

* Can send but doesn't receive ``active_sensing`` messages.

* No callback mechanism so callbacks are implemented in
  Python with threads. Each port with a callback has a dedicated thread
  doing blocking reads from the device.

* Due to limitations in PortMidi the port list will not be up-to-date if
  there are any ports open. (The refresh is implemented by
  re-initializing PortMidi which would break any open ports.)
