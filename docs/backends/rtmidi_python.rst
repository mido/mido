.. SPDX-FileCopyrightText: 2013 Ole Martin Bjorndalen <ombdalen@gmail.com>
..
.. SPDX-License-Identifier: CC-BY-4.0

rtmidi_python
-------------

Name: ``mido.backends.rtmidi_python``

Resources:

* `rtmidi-python Python Library <https://pypi.org/project/rtmidi-python/>`_


Installing
^^^^^^^^^^

::

    python3 - m pip install rtmidi-python


Features
^^^^^^^^

* uses the ``rtmidi_python`` package rather than ``python-rtmidi``

* supports callbacks

* limited support for virtual ports (no client name)

* no true blocking

* sends but doesn't receive ``active sensing``

.. todo::

    Since the API of ``rtmidi_python`` and ``python-rtmidi`` are almost
    identical it would make sense to refactor so they share most of the
    code.
