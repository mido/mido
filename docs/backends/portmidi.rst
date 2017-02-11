PortMidi
--------

Name: ``mido.backends.portmidi``

Features:

The PortMidi backend is written with ``ctypes`` and requires only the
shared library file ``portmidi.so`` or ``portmidi.dll``.

Can send but doesn't receive ``active_sensing`` messages.

PortMidi has no callback mechanism, so callbacks are implemented in
Python with threads. Each port with a callback has a dedicated thread
doing blocking reads from the device.

Due to limitations in PortMidi the port list will not be up-to-date if
there are any ports open. (The refresh is implemented by
re-initalizing PortMidi which would break any open ports.)
