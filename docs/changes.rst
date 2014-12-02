Changes
=======

Release History
---------------

1.1.12 (2014-12-02)
^^^^^^^^^^^^^^^^^^^

* raises IOError if you try to open a virtual port with PortMIDI or
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
  will end there instead of at the preceeding message.


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
  on a PortMIDI input. (Issue #15, reported by Francesco Ceruti.)

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
