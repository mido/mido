PortMidi
--------

Name: ``mido.backends.portmidi``


Installing
^^^^^^^^^^

The PortMidi backend requires the ``portmidi`` shared library.

`Ubuntu <https://www.ubuntu.com/>`_::

    apt install libportmidi-dev

`Homebrew <http://mxcl.github.io/homebrew/>`_::

    brew install portmidi

`MacPorts <http://www.macports.org/>`_::

    port install portmidi

The backend will look for::

    portmidi.so      (Linux)
    portmidi.dll     (Windows)
    portmidi.dynlib  (macOS)


Features
^^^^^^^^

Can send but doesn't receive ``active_sensing`` messages.

PortMidi has no callback mechanism, so callbacks are implemented in
Python with threads. Each port with a callback has a dedicated thread
doing blocking reads from the device.

Due to limitations in PortMidi the port list will not be up-to-date if
there are any ports open. (The refresh is implemented by
re-initalizing PortMidi which would break any open ports.)
