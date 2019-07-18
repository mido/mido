Changes
=======

(See :doc:`roadmap` for future plans.)


Release History
---------------

1.2.10
^^^^^^^^^^^^^^^^^^

* Improved MidiFile.play to avoid time drift. (Implemented by John
  Belmonte, pull request #161.)

* New ``repr()`` format. (Original implementation by John Belmonte,
  pull request #164.)

* bugfix: MIDO_DEFAULT_INPUT was misspelled in mido-ports causing it
  to be show as 'not set' even though it was set. (Fix by Bernhard
  Wagner, pull request #192.)

* Updated linke in docs to point to the new home github.com/mido/
  (Fixed by Joshua Mayers, pull request #177.)



1.2.9 (2018-10-05)
^^^^^^^^^^^^^^^^^^

* rewrote ``Parser`` class around a MIDI tokenizer. Should lead to
  slight speedup and much cleaner code.

* bugfix: `data` attribute was missing for `UnknownMetaMessage`
  objects. This caused `AttributeError` when the messages were printed
  or saved to a file. Also, the documentation incorrectly listed the
  attribute as `_data` instead of `data`. (Reported by Groowy.)

* bugfix: UnknownMetaMessage encoding was broken causing crashes when
  saving a file with unknown meta messages. (Reported by exeex, issue
  #159.)

* bugfix: inputs and outputs were switched around when opening named
  ports with PortMidi backend. (Reproduced by Predrag Radovic, issue
  #108, fix by Juan Antonio Aldea, pull request #109.)

* bugfix: time signature meta messages had wrong default value of
  2/4. The default value is now 4/4. (Fix by Sebastian Böck, pull
  request #104.)

* bugfix: ``msg.copy()`` didn't handle generators for sysex
  data. ``msg.copy(data=(i for i in range(3)))`` would give
  ``data=()`` instead of ``data=(0,1,2)``.

  (The code should be refactored so this is handled by the same
  function everywhere, such as in ``__init__()``, in ``copy()`` and in
  ``parser.feed()``.)

* bugfix: ``MultiPort._receive()`` ignored the ``block``
  parameter. (Fix by Tom Swirly, pull request #135.)

* bugfix: sequencer number meta message was incorrectly limited to
  range 0..255 instead of 0..65335. (Reported by muranyia, issue
  #144.)

* now using Tox for testing. (Implemented by Chris Apple, pull request
  #123.)

* Travis integration up by Carl Thomé and Chris Apple.


1.2.8 (2017-06-30)
^^^^^^^^^^^^^^^^^^

* bugfix: nonblocking receive was broken for RtMidi IO
  ports. (Reported by Chris Apple, issue #99.)

* bugfix: ``IOPort.poll()`` would block if another thread was waiting
  for ``receive()``.  Fixed the problem by removing the lock, which
  was never needed in the first place as the embedded input port does
  its own locking.


1.2.7 (2017-05-31)
^^^^^^^^^^^^^^^^^^
* added max length when reading message from a MIDI file. This
  prevents Python from running out of memory when reading a corrupt
  file. Instead it will now raise an ``IOError`` with a descriptive
  error message. (Implemented by Curtis Hawthorne, pull request #95.)

* removed dependency on ``python-rtmidi`` from tests. (Reported by
  Josue Ortega, issue #96.)


1.2.6 (2017-05-04)
^^^^^^^^^^^^^^^^^^

* bugfix: Sending sysex with Pygame in Python 3 failed with
  ``"TypeError: array() argument 1 must be a unicode character, not
  byte"``.  (Reported by Harry Williamson.)

* now handles ``sequence_number`` and ``midi_port`` messages with 0
  data bytes. These are incorrect but can occur in rare cases. See
  ``mido/midifiles/test_midifiles.py`` for more. (Reported by Gilthans
  (issue #42) and hyst329 (issue #93)).


1.2.5 (2017-04-28)
^^^^^^^^^^^^^^^^^^

* bugfix: RtMidi backend ignored ``api`` argument. (Fix by Tom Feist,
  pull request #91.)


1.2.4 (2017-03-19)
^^^^^^^^^^^^^^^^^^

* fixed outdated python-rtmidi install instructions. (Reported by
  Christopher Arndt, issue #87.)


1.2.3 (2017-03-14)
^^^^^^^^^^^^^^^^^^

* typo and incorrect links in docs fixed by Michael (miketwo) (pull requests
  #84 and #85).


1.2.2 (2017-03-14)
^^^^^^^^^^^^^^^^^^

* bugfix: sysex data was broken in string format encoding and decoding.
  The data was encoded with spaces ('data=(1, 2, 3)') instead of as one word
  ('data=(1,2,3)').

* added some tests for string format.

* bugfix: ``BaseOutput.send()`` raised string instead of ``ValueError``.


1.2.1 (2017-03-10)
^^^^^^^^^^^^^^^^^^

* bugfix: IO port never received anything when used with RtMidi
  backend. (Reported by dagargo, issue #83.)

  This was caused by a very old bug introduced in 1.0.3. IOPort
  mistakenly called the inner method ``self.input._receive()`` instead
  of ``self.input.receive()``. This happens to work for ports that
  override ``_receive()`` but not for the new RtMidi backend which
  overrides ``receive()``. (The default implementation of
  ``_receive()`` just drops the message on the floor.)

* bugfix: PortMidi backend was broken due to missing import
  (``ctypes.byref``). (Introduced in 1.2.0.)


1.2.0 (2017-03-07)
^^^^^^^^^^^^^^^^^^^

New implementation of messages and parser:

* completely reimplemented messages. The code is now much simpler,
  clearer and easier to work with.

* new contructors ``Message.from_bytes()``, ``Message.from_hex()``,
  ``Message.from_str()``.

* new message attributes ``is_meta`` and ``is_realtime``.


Frozen (immutable) messages:

* added ``FrozenMessage`` and ``FrozenMetaMessage``. These are
  immutable versions of ``Message`` and ``MetaMessage`` that are
  hashable and thus can be used as dictionary keys. These are
  available in ``mido.frozen``. (Requested by Jasper Lyons, issue
  #36.)


RtMidi is now the default backend:

* switched default backend from PortMidi to RtMidi. RtMidi is easier
  to install on most systems and better in every way.

  If you want to stick to PortMidi you can either set the environment
  variable ``$MIDO_BACKEND=mido.backends.portmidi`` or call
  ``mido.set_backend('mido.backends.portmidi')`` in your program.

* refactored the RtMidi backend to have a single ``Port`` class
  instead of inheriting from base ports. It was getting hard to keep
  track of it all. The code is now a lot easier to reason about.

* you can now pass ``client_name`` when opening RtMidi ports:
  ``open_output('Test', client_name='My Client')``. When
  ``client_name`` is passed the port will automatically be a virtual
  port.

* with ``LINUX_ALSA`` you can now omit client name and ALSA
  client/port number when opening ports, allowing you to do
  ``mido.open_output('TiMidity port 0')`` instead of
  ``mido.open_output('TiMidity:TiMidity port 0 128:0')``. (See RtMidi
  backend docs for more.)


Changes to the port API:

* ports now have ``is_input`` and ``is_output`` attributes.

* new functions ``tick2second()`` and ``second2tick()``. (By Carl
  Thomé, pull request #71.)

* added ``_locking`` attribute to ``BasePort``. You can set this to
  ``False`` in a subclass to do your own locking.

* ``_receive()`` is now allowed to return a messages. This makes the
  API more consistent and makes it easier to implement thread safe
  ports.

* ``pending()`` is gone. This had to be done to allow for the new
  ``_receive()`` behavior.

* improved MIDI file documentation. (Written by Carl Thomé.)


Other changes:

* bugfix: if a port inherited from both ``BaseInput`` and
  ``BaseOutput`` this would cause ``BasePort.__init__()`` to be called
  twice, which means ``self._open()`` was also called twice. As a
  workaround ``BasePort.__init__()`` will check if ``self.closed``
  exists.

* added ``mido.version_info``.

* ``mido.set_backend()`` can now be called with ``load=True``.

* added ``multi_send()``.

* ``MIN_PITCHWHEEL``, ``MAX_PITCHWHEEL``, ``MIN_SONGPOS`` and
  ``MAX_SONGPOS`` are now available in the top level module (for
  example ``mido.MIN_PITCHWHEEL``).

* added experimental new backend ``mido.backends.amidi``. This uses
  the ALSA ``amidi`` command to send and receive messages, which makes
  it very inefficient but possibly useful for sysex transfer.

* added new backend ``mido.backends.rtmidi_python`` (previously
  available in the examples folder.) This uses the ``rtmidi-python``
  package instead of ``python-rtmidi``. For now it lacks some of
  features of the ``rtmidi`` backend, but can still be useful on
  systems where ``python-rtmidi`` is not available. (Requested by
  netchose, issue #55.)


1.1.24 (2017-02-16)
^^^^^^^^^^^^^^^^^^^

* bugfix: PortMidi backend was broken on macOS due to a typo. (Fix by
  Sylvain Le Groux, pull request #81.)


1.1.23 (2017-01-31)
^^^^^^^^^^^^^^^^^^^

* bugfix: ``read_syx_file()`` didn't handle '\n' in text format file
  causing it to crash. (Reported by Paul Forgey, issue #80.)


1.1.22 (2017-01-27)
^^^^^^^^^^^^^^^^^^^

* the bugfix in 1.1.20 broke blocking receive() for RtMidi. Reverting
  the changes. This will need some more investigation.


1.1.21 (2017-01-26)
^^^^^^^^^^^^^^^^^^^

* bugfix: MidiFile save was broken in 1.1.20 due to a missing import.


1.1.20 (2017-01-26)
^^^^^^^^^^^^^^^^^^^

* bugfix: close() would sometimes hang for RtMidi input ports. (The
  bug was introduced in 1.1.18 when the backend was rewritten to
  support true blocking.)

* Numpy numbers can now be used for all message attributes. (Based on
  implementation by Henry Mao, pull request #78.)

  The code checks against numbers.Integral and numbers.Real (for the
  time attribute) so values can be any subclass of these.


1.1.19 (2017-01-25)
^^^^^^^^^^^^^^^^^^^

* Pygame backend can now receive sysex messages. (Fix by Box of Stops.)

* bugfix: ``libportmidi.dylib`` was not found when using
  MacPorts. (Fix by yam655, issue #77.)

* bugfix: ``SocketPort.__init()`` was not calling
  ``IOPort.__init__()`` which means it didn't get a
  ``self._lock``. (Fixed by K Lars Lohn, pull request #72. Also
  reported by John J. Foerch, issue #79.)

* fixed typo in intro example (README and index.rst). Fix by Antonio
  Ospite (pull request #70), James McDermott (pull request #73) and
  Zdravko Bozakov (pull request #74).

* fixed typo in virtual ports example (Zdravko Bozakov, pull request #75.)


1.1.18 (2016-10-22)
^^^^^^^^^^^^^^^^^^^

* ``time`` is included in message comparison. ``msg1 == msg2`` will
  now give the same result as ``str(msg1) == str(msg2)`` and
  ``repr(msg1)`` == ``repr(msg2)``.

  This means you can now compare tracks wihout any trickery, for
  example: ``mid1.tracks == mid2.tracks``.

  If you need to leave out time the easiest was is ``msg1.bytes() ==
  msg2.bytes()``.

  This may in rare cases break code.

* bugfix: ``end_of_track`` messages in MIDI files were not handled correctly.
  (Reported by Colin Raffel, issue #62).

* bugfix: ``merge_tracks()`` dropped messages after the first
  ``end_of_track`` message. The new implementation removes all
  ``end_of_track`` messages and adds one at the end, making sure to
  adjust the delta times of the remaining messages.

* refactored MIDI file code.

* ``mido-play`` now has a new option ``-m / --print-messages`` which
  prints messages as they are played back.

* renamed ``parser._parsed_messages`` to
  ``parser.messages``. ``BaseInput`` and ``SocketPort`` use it so it
  should be public.

* ``Parser()`` now takes an option argument ``data`` which is passed
  to ``feed()``.


1.1.17 (2016-10-06)
^^^^^^^^^^^^^^^^^^^

* RtMidi now supports true blocking ``receive()`` in Python 3. This
  should result in better performance and lower latency. (Thanks to
  Adam Roberts for helping research queue behavior. See issue #49 for
  more.)

* bugfix: ``MidiTrack.copy()`` (Python 3 only) returned ``list``.

* fixed example ``queue_port.py`` which broke when locks where added.


1.1.16 (2016-09-27)
^^^^^^^^^^^^^^^^^^^

* bugfix: ``MidiTrack`` crashed instead of returning a message on
  ``track[index]``. Fix by Colin Raffel (pull request #61).

* added ``__add__()`` and ``__mul__()`` to ``MidiTrack`` so ``+`` and
  ``*`` will return tracks instead of lists.

* added ``poll()`` method to input ports as a shortcut for
  ``receive(block=False)``.

* added example ``rtmidi_python_backend.py``, a backend for the
  rtmidi-python package (which is different from the python-rtmidi
  backend that Mido currently uses.) This may at some point be added
  to the package but for now it's in the examples folder. (Requested
  by netchose, issue #55.)

* removed custom ``_import_module()``. Its only function was to make
  import errors more informative by showing the full module path, such
  as ``ImportError: mido.backends.rtmidi`` instead of just ``ImportError:
  rtmidi``. Unfortunately it ended up masking import errors in the
  backend module, causing confusion.

  It turns ``importlib.import_module()`` can be called with the full
  path, and on Python 3 it will also display the full path in the
  ``ImportError`` message.


1.1.15 (2016-08-24)
^^^^^^^^^^^^^^^^^^^

* Sending and receiving messages is now thread safe. (Initial
  implementation by Adam Roberts.)

* Bugfix: ``PortServer`` called ``__init__`` from the wrong
  class. (Fix by Nathan Hurst.)

* Changes to ``MidiTrack``:

  * ``MidiTrack()`` now takes a as a parameter an iterable of
    messages. Examples:

    .. code-block:: python

        MidiTrack(messages)
        MidiTrack(port.iter_pending())
        MidiTrack(msg for msg in some_generator)

  * Slicing a ``MidiTrack`` returns a ``MidiTrack``. (It used to
    return a ``list``.) Example:

    .. code-block:: python

        track[1:10]

* Added the ability to use file objects as well as filenames when reading,
  writing and saving MIDI files. This allows you to create a MIDI file
  dynamically, possibly *not* using mido, save it to an io.BytesIO, and
  then play that in-memory file, without having to create an intermediate
  external file. Of course the memory file (and/or the MidiFile) can still
  be saved to an external file.
  (Implemented by Brian O'Neill.)

* PortMidi backend now uses pm.lib.Pm_GetHostErrorText() to get host
  error messages instead of just the generic "PortMidi: \`Host error\'".
  (Implemented by Tom Manderson.)

Thanks to Richard Vogl and Tim Cook for reporting errors in the docs.


1.1.14 (2015-06-09)
^^^^^^^^^^^^^^^^^^^

* bugfix: merge_tracks() concatenated the tracks instead of merging
  them.  This caused tracks to be played back one by one. (Issue #28,
  reported by Charles Gillingham.)

* added support for running status when writing MIDI files.
  (Implemented by John Benediktsson.)

* rewrote the callback system in response to issues #23 and #25.

* there was no way to set a callback function if the port was opened
  without one. (Issue#25, reported by Nils Werner.)

  Callbacks can now be set and cleared at any time by either passing
  one to ``open_input()`` or updating the ``callback`` attribute.

  This causes some slight changes to the behavior of the port when
  using callbacks. Previously if you opened the port with a callback
  and then set ``port.callback = None`` the callback thread would keep
  running but drop any incoming messages. If you do the same now the
  callback thread will stop and the port will return normal
  non-callback behavior. If you want the callback thread to drop
  messages you can set ``port.callback = lambda message: None``.

  Also, ``receive()`` no longer checks ``self.callback``. This was
  inconsistent as it was the only method to do so. It also allows
  ports that don't support callbacks to omit the ``callback``
  attribute.

* bugfix: closing a port would sometimes cause a segfault when using
  callbacks. (Issue #24, reported by Francesco Ceruti.)

* bugfix: Pygame ports were broken due to a faulty check for ``virtual=True``.

* now raises ``ValueError`` instead of ``IOError`` if you pass
  ``virtual`` or ``callback`` while opening a port and the backend
  doesn't support them. (An unsupported argument is not an IO error.)

* fixed some errors in backend documentation. (Pull request #23 by
  velolala.)

* ``MultiPort`` now has a ``yield_port`` argument just like
  ``multi_receive()``.


1.1.13 (2015-02-07)
^^^^^^^^^^^^^^^^^^^

* the PortMidi backend will now return refresh the port list when you
  ask for port names are open a new port, which means you will see
  devices that you plug in after loading the backend. (Due to
  limitations in PortMidi the list will only be refreshed if there are
  no open ports.)

* bugfix: ``tempo2bpm()`` was broken and returned the wrong value for
  anything but 500000 microseconds per beat (120 BPM). (Reported and
  fixed by Jorge Herrera, issue #21)

* bugfix: ``merge_tracks()`` didn't work with empty list of tracks.

* added proper keyword arguments and doc strings to open functions.


1.1.12 (2014-12-02)
^^^^^^^^^^^^^^^^^^^

* raises IOError if you try to open a virtual port with PortMidi or
  Pygame. (They are not supported by these backends.)

* added ``merge_tracks()``.

* removed  undocumented method ``MidiFile.get_messages()``.
  (Replaced by ``merge_tracks(mid.tracks)``.)

* bugfix: ``receive()`` checked ``self.callback`` which didn't exist
  for all ports, causing an ``AttributeError``.


1.1.11 (2014-10-15)
^^^^^^^^^^^^^^^^^^^

* added ``bpm2tempo()`` and ``tempo2bpm()``.

* fixed error in documentation (patch by Michael Silver).

* added notes about channel numbers to documentation (reported by
  ludwig404 / leonh, issue #18).


1.1.10 (2014-10-09)
^^^^^^^^^^^^^^^^^^^

* bugfix: MidiFile.length was computer incorrectly.

* bugfix: tempo changes caused timing problems in MIDI file playback.
  (Reported by Michelle Thompson.)

* mido-ports now prints port names in single ticks.

* MidiFile.__iter__() now yields end_of_track. This means playback
  will end there instead of at the preceding message.


1.1.9 (2014-10-06)
^^^^^^^^^^^^^^^^^^

* bugfix: _compute_tick_time() was not renamed to
  _compute_seconds_per_tick() everywhere.

* bugfix: sleep time in play() was sometimes negative.


1.1.8 (2014-09-29)
^^^^^^^^^^^^^^^^^^

* bugfix: timing in MIDI playback was broken from 1.1.7 on.  Current
  time was subtracted before time stamps were converted from ticks to
  seconds, leading to absurdly large delta times. (Reported by Michelle
  Thompson.)

* bugfix: ``read_syx_file()`` didn't handle empty file.


1.1.7 (2014-08-12)
^^^^^^^^^^^^^^^^^^

* some classes and functions have been moved to more accessible locations::

    from mido import MidiFile, MidiTrack, MetaMessage
    from mido.midifiles import MetaSpec, add_meta_spec

* you can now iterate over a MIDI file. This will generate all MIDI
  messages in playback order. The ``time`` attribute of each message
  is the number of seconds since the last message or the start of the
  file. (Based on suggestion by trushkin in issue #16.)

* added get_sleep_time() to complement set_sleep_time().

* the Backend object no longer looks for the backend module exists on
  startup, but will instead just import the module when you call one
  of the ``open_*()`` or ``get_*()`` functions. This test didn't work
  when the library was packaged in a zip file or executable.

  This means that Mido can now be installed as Python egg and frozen
  with tools like PyInstaller and py2exe. See "Freezing Mido Programs"
  for more on this.

  (Issue #17 reported by edauenhauer and issue #14 reported by
  netchose.)

* switched to pytest for unit tests.


1.1.6 (2014-06-21)
^^^^^^^^^^^^^^^^^^

* bugfix: package didn't work with easy_install.
  (Issue #14, reported by netchose.)

* bugfix: 100% memory consumption when calling blocking receive()
  on a PortMidi input. (Issue #15, reported by Francesco Ceruti.)

* added wheel support: http://pythonwheels.com/


1.1.5 (2014-04-18)
^^^^^^^^^^^^^^^^^^

* removed the 'mode' attribute from key_signature messages. Minor keys
  now have an 'm' appended, for example 'Cm'.

* bugfix: sysex was broken in MIDI files.

* bugfix: didn't handle MIDI files without track headers.

* bugfix: MIDI files didn't handle channel prefix > 15

* bugfix: MIDI files didn't handle SMPTE offset with frames > 29


1.1.4 (2014-10-04)
^^^^^^^^^^^^^^^^^^

* bugfix: files with key signatures Cb, Db and Gb failed due to faulty
  error handling.

* bugfix: when reading some MIDI files Mido crashed with the message
  "ValueError: attribute must be in range 0..255". The reason was that
  Meta messages set running status, which caused the next statusless
  message to be falsely interpreted as a meta message. (Reported by
  Domino Marama).

* fixed a typo in MidiFile._read_track(). Sysex continuation should
  work now.

* rewrote tests to make them more readable.


1.1.3 (2013-10-14)
^^^^^^^^^^^^^^^^^^

* messages are now copied on send. This allows the sender to modify the
  message and send it to another port while the two ports receive their
  own personal copies that they can modify without any side effects.


1.1.2 (2013-10-05)
^^^^^^^^^^^^^^^^^^

* bugfix: non-ASCII character caused trouble with installation when LC_ALL=C.
  (Reported by Gene De Lisa)

* bugfix: used old exception handling syntax in rtmidi backend which
  broke in 3.3

* fixed broken link in


1.1.1 (2013-10-04)
^^^^^^^^^^^^^^^^^^

* bugfix: mido.backends package was not included in distribution.


1.1.0 (2013-10-01)
^^^^^^^^^^^^^^^^^^

* added support for selectable backends (with MIDO_BACKEND) and
  included python-rtmidi and pygame backends in the official library
  (as mido.backend.rtmidi and mido.backend.pygame).

* added full support for MIDI files (read, write playback)

* added MIDI over TCP/IP (socket ports)

* added utility programs mido-play, mido-ports, mido-serve and mido-forward.

* added support for SMPTE time code quarter frames.

* port constructors and ``open_*()`` functions can now take keyword
  arguments.

* output ports now have reset() and panic() methods.

* new environment variables MIDO_DEFAULT_INPUT, MIDO_DEFAULT_OUTPUT
  and MIDO_DEFAULT_IOPORT. If these are set, the open_*() functions
  will use them instead of the backend's default ports.

* added new meta ports MultiPort and EchoPort.

* added new examples and updated the old ones.

* format_as_string() now takes an include_time argument (defaults to True)
  so you can leave out the time attribute.

* sleep time inside sockets can now be changed.

* Message() no longer accepts a status byte as its first argument. (This was
  only meant to be used internally.)

* added callbacks for input ports (PortMidi and python-rtmidi)

* PortMidi and pygame input ports now actually block on the device
  instead of polling and waiting.

* removed commas from repr() format of Message and MetaMessage to make
  them more consistent with other classes.


1.0.4 (2013-08-15)
^^^^^^^^^^^^^^^^^^

* rewrote parser


1.0.3 (2013-07-12)
^^^^^^^^^^^^^^^^^^

* bugfix: __exit__() didn't close port.

* changed repr format of message to start with "message".

* removed support for undefined messages. (0xf4, 0xf5, 0xf7, 0xf9 and 0xfd.)

* default value of velocity is now 64 (0x40).
  (This is the recommended default for devices that don't support velocity.)


1.0.2 (2013-07-31)
^^^^^^^^^^^^^^^^^^

* fixed some errors in the documentation.


1.0.1 (2013-07-31)
^^^^^^^^^^^^^^^^^^

* multi_receive() and multi_iter_pending() had wrong implementation.
  They were supposed to yield only messages by default.


1.0.0 (2013-07-20)
^^^^^^^^^^^^^^^^^^

Initial release.

Basic functionality: messages, ports and parser.
