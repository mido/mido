Roadmap
=======

This will be developed into a proper roadmap but for now it's more of a list of ideas.


Near Future
-----------

* create a place for general discussion, for example a google group
  (mido-discuss and perhaps a separate mido-dev).

* a `PEP <https://www.python.org/dev/peps/>`_ like process for new
  features and major changes.



Ideas
-----


Making Messages Immutable
^^^^^^^^^^^^^^^^^^^^^^^^^

See: https://github.com/olemb/mido/issues/36

The current workaround is frozen messages (``mido.freeze``).

In any case, the documentation should be updated to encourage copying
over mutation.



Native Backends (ALSA, JACK, CoreMIDI, Windows MIDI)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

See https://github.com/olemb/mido-native-backends


No Default Backend?
^^^^^^^^^^^^^^^^^^^

Currently one backend is chosen as the default. Perhaps it would be
better to require the user to specify the backend with
``$MIDO_BACKEND`` or ``mido.set_backend()``.


New API for Creating New Port Types
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The current system uses multiple inheritance making the code very hard
to follow and reason about.

In the RtMidi backend I've experimented with a mixin-based system. You
write the basic port and then use inheritance to "import" more methods
into your class:

.. code-block:: python

    class Input(PortMethods, InputMethods):
        def receive(self):
            ...        

        # __repr__(),

The downside is that you have to manage things like ``closed`` and
``autoreset`` behaviour leading to this boilerplate in every class:

        def __init__(self, name=None, autoreset=False, **kwargs):
            self.name = name
            self.closed = False
            self.autoreset = False
            ...

        def send(self, msg):
	    ...

  	def close(self):
	    if not closed:
                ...
                self.closed = False

You also have to add doc strings to ``send()`` and ``receive()``.

The upside is that you have full control of what your class does.
