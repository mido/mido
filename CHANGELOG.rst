1.1 -
------

* implemented MIDI files (mido.midifiles).

* implemented MIDI over TCP/IP (socket ports) (mido.sockets).

* added support for SMPTE time code quarter frames.

* output ports now have reset() and panic() methods.


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
