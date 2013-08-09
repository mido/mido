1.1 -
------

* added full support for MIDI files (read, write playback)

* added MIDI over TCP/IP (socket ports)

* added support for selectable backends (with MIDO_BACKEND) and
  included python-rtmidi and pygame backends in the official library
  (as mido.backend.rtmidi and mido.backend.pygame).

* backend API simplified to so that you only need to implement
  get_device(), Input and Output, and optionally IOPort. All of these
  are optional, depending on how the backend will be used and what
  functionality it provices.

* added utility programs mido-play, mido-ports, mido-serve and mido-forward.

* added support for SMPTE time code quarter frames.

* port constructors can now take keyword arguments.

* output ports now have reset() and panic() methods.

* new environment variables MIDO_DEFAULT_INPUT, MIDO_DEFAULT_OUTPUT
  and MIDO_DEFAULT_IOPORT. If these are set, the open_*() functions
  will use them instead of the backend's default ports.

* added ports.Broadcast, a port contains a list of ports and
  sends its messages to all of these.

* added new examples and updated the old ones.

* format_as_string() now takes an include_time argument (defaults to True)
  so you can leave out the time attribute.

* added new virtual ports MultiPort and EchoPort.

* sleep time in poll and wait inside sockets can now be changed.

* removed the message type 'sysex_end'. It had no use and only caused problems.

* Message() no longer accepts a status byte as its first argument. (This was
  only meant to be used internally.)

* message creation is heavily optimized.


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
