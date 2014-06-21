1.1.6 - 2014-06-21
-------------------

* bugfix: package didn't work with easy_install.
  (Issue #14, reported by netchose.)

* bugfix: 100% memory consumption when calling blocking receive()
  on a PortMIDI input. (Issue #15, reported by Francesco Ceruti.)

* added wheel support: http://pythonwheels.com/


1.1.5 - 2014-04-18
-------------------

* removed the 'mode' attribute from key_signature messages. Minor keys
  now have an 'm' appended, for example 'Cm'.

* bugfix: sysex was broken in MIDI files.

* bugfix: didn't handle MIDI files without track headers.

* bugfix: MIDI files didn't handle channel prefix > 15 

* bugfix: MIDI files didn't handle SMPTE offset with frames > 29


1.1.4 - 2014-10-04
-------------------

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


1.1.3 - 2013-10-14
-------------------

* messages are now copied on send. This allows the sender to modify the
  message and send it to another port while the two ports receive their
  own personal copies that they can modify without any side effects.


1.1.2 - 2013-10-05
-------------------

* bugfix: non-ASCII character caused trouble with installation when LC_ALL=C.
  (Reported by Gene De Lisa)

* bugfix: used old exception handling syntax in rtmidi backend which
  broke in 3.3

* fixed broken link in 


1.1.1 - 2013-10-04
-------------------

* bugfix: mido.backends package was not included in distribution.


1.1 - 2013-10-01
-----------------

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


1.0.4 - 2013-08-15
-------------------

* rewrote parser


1.0.3 - 2013-07-12
-------------------

* bugfix: __exit__() didn't close port.

* changed repr format of message to start with "message".

* removed support for undefined messages. (0xf4, 0xf5, 0xf7, 0xf9 and 0xfd.)

* default value of velocity is now 64 (0x40).
  (This is the recommended default for devices that don't support velocity.)


1.0.2 - 2013-07-31
-------------------

* fixed some errors in the documentation.


1.0.1 - 2013-07-31 - bugfix
----------------------------

* multi_receive() and multi_iter_pending() had wrong implementation.
  They were supposed to yield only messages by default.

1.0 - 2013-07-20 - initial release
-------------------------------------

Basic functionality: messages, ports and parser.
