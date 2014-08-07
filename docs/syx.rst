SYX Files
=========

SYX files are used to store SysEx messages, most often for patch
data.


Reading and Writing
-------------------

To read a SYX file::

    messages = mido.read_syx('patch.syx')

To write a SYX file::

    mido.write_syx('patch.syx', messages)


Plain Text Format
-----------------

Mido also supports plain text SYX files. These are read in exactly the
same way::

    messages = mido.read_syx('patch.txt')

``read_syx()`` determins which format the file is by looking at the
first byte.

To write plain text::

    mido.write_syx('patch.txt', messages, plaintext=True)
