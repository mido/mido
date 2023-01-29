SYX Files
=========

SYX files are used to store SysEx messages, usually for patch
data.


Reading and Writing
-------------------

To read a SYX file::

    messages = mido.read_syx_file('patch.syx')

To write a SYX file::

    mido.write_syx_file('patch.syx', messages)

Non-sysex messages will be ignored.


Plain Text Format
-----------------

Mido also supports plain text SYX files. These are read in exactly the
same way::

    messages = mido.read_syx_file('patch.txt')

``read_syx_file()`` determines which format the file is by looking at
the first byte.  It Raises ValueError if file is plain text and byte
is not a 2-digit hex number.

To write plain text::

    mido.write_syx_file('patch.txt', messages, plaintext=True)

This will write the messages as hex encoded bytes with one message per
line::

    F0 00 01 5D 02 00 F7
    F0 00 01 5D 03 00 F7
