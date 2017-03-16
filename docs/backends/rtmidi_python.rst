rtmidi_python
-------------

Name: ``mido.backends.rtmidi_python``


Installing
^^^^^^^^^^

::

    pip install rtmidi-python


Features
^^^^^^^^

* uses the ``rtmidi_python`` package rather than ``python_rtmidi``

* supports callbacks

* limited support for virtual ports (no client name)

* no true blocking

* sends but doesn't receive active sensing

Since the API of ``rtmidi_python`` and ``python_rtmidi`` are almost
identical it would make sense to refactor so they share most of the
code.
