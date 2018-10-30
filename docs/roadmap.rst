Roadmap
=======

This will be developed into a proper roadmap but for now it's more of
a list of ideas.


Near Future
-----------

* create a place for general discussion:
  Now exists: https://groups.google.com/forum/#!forum/mido-community

* a `PEP <https://www.python.org/dev/peps/>`_ like process for new
  features and major changes?


Various Improvements to MIDI File Parsing
-----------------------------------------

* add ``mido.exceptions.MidiParseError``.

* add better error handling to MIDI file parser as discussed in `issue
  #63 <https://github.com/mido/mido/issues/63>`_.

* support RIFF MIDI files (`issue #43
  <https://github.com/mido/mido/issues/43>`_)

* support MIDI files that end in empty meta message
  (`issue #42 <https://github.com/mido/mido/issues/42>`_)


Better Support for Concurrency and Multithreading
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Mido was not originally designed for multithreading. Locks were added
to the port base classes as an attempt to get around this but it is a
crude solution that has created numerous problems and headaches.

The RtMido backend has abandoned locking in favor of using RtMidi's
user callback to feed a queue. If you write your port so that
``send()``, ``receive()`` and ``poll()`` are thread safe the rest of
the rest of the API will be as well.

For ports that do actual I/O (MIDI devices, sockets, files, pipes
etc.) it is always best for the port itself to ensure thread
safety. It's less clear what to do for utility ports like
``MultiPort``.

Mido is currently not very good at multiplexing input. You can use
``MultiPort`` and ``multi_receive()``, but since it can't actually
block on more than one port it uses poll and wait. This uses more
resources and adds latency.

The alternative is to use callbacks, but only a few backends support
(and some like PortMidi fake them with a thread that polls and waits,
taking you back to square one). Programming with callbacks also forces
you to deal with multithreading (since the callback runs in a
different thread) and to break your program flow up into callback
handlers. This is not always desirable.

In Go the solution would be to use channels instead of ports. Each
port would then have its own channel with a goroutine reading from the
device and feeding the channel, and the language would take care of
the multiplexing. I am not sure how one would achieve something like
this in Python.


Making Messages Immutable
^^^^^^^^^^^^^^^^^^^^^^^^^

See: https://github.com/mido/mido/issues/36

The current workaround is frozen messages (``mido.freeze``).

In any case, the documentation should be updated to encourage copying
over mutation.



Native Backends (ALSA, JACK, CoreMIDI, Windows MIDI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See https://github.com/mido/mido-native-backends


No Default Backend?
^^^^^^^^^^^^^^^^^^^

Currently one backend is chosen as the default. Perhaps it would be
better to require the user to specify the backend with
``$MIDO_BACKEND`` or ``mido.set_backend()``.


New API for Creating New Port Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The current system uses multiple inheritance making the code very hard
to follow and reason about:

* too much magic and too much you need to keep in your head

* attributes like ``self.name`` and ``self.closed`` appear in your
  name space and you have to dig around in the base classes to see
  where they come from

* there is a ``self._parser`` in every port even if you don't need it

* ``self._parser`` is not thread safe

* ``BaseInput.receive()`` needs to account for all the numerous
  current and historical behaviors of ``self._receive()``.

* blocking and nonblocking receive can not be protected by the same
  lock (since a call to ``receive()`` would then block a call to
  ``poll()``), which means ports that due true blocking need to do
  their own locking.

* if you want to do our own locking you need to remember to set
  ``_locking=False``. This will replace the lock with a dummy lock,
  which while doing nothing still adds a bit of overhead.

A good principle is for any part of the code to know as little as
possible about the rest of the code. For example a backend port should
only need to worry about:

* opening and closing the device

* reading and writing data (blocking and nonblocking)

It should not have to worry about things like ``autoreset``,
``closed=True/False`` and iteration. Also, as long as its ``send()``
and ``receive()/poll()`` methods are thread safe the rest of the API
will be as well.

Some alternatives to subclassing:

* embedding: write a basic port and wrap it in a ``FancyPort`` which
  provides the rest of the API

* mixins: write a basic port and use mixins (``PortMethods``,
  ``InputMethods``, ``OutputMethods``) to import the rest of the API.


Maybe
-----

* add a way to convert between MIDI file types as suggested in `issue
  #92 <https://github.com/mido/mido/issues/92>`_.

* RtMidi backend: allow user to list ports without client name and
  ALSA port numbers.

* Add native backends? See https://github.com/mido/mido-native-backends

* Currently all backends ignore ``active_sensing`` messages because
  they create a lot of noise and are usually not very useful. Should
  this be changed (perhaps as an option)?

  Filtering can be turned off with:

  * rtmidi: ``self._rt.ignore_types(False, False, False)``

  * portmidi: ``pm.lib.Pa_SetFilter(self._stream, 0)``

  * rtmidi_python: ``self._rt.ignore_types(False, False, False)``

  * pygame: (is there a way to configure this?)

  * amidi: (not sure if this receives ``active_sensing`` already)

* Refactor ``rtmidi`` and ``rtmidi_python`` backends to avoid code
  duplication. This would give ``rtmidi_python`` all of the features
  of ``rtmidi`` (as long as they are supported in the package).

* Add more fine grained error types, for example ``PortNotFound``
  instead of just ``IOError``. (This should be a subclass so old code
  still works.) One problem here is that new code that uses
  ``PortNotFound`` would not work with backends that raise ``IOError``.
