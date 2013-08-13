1.0.4 -
--------

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
