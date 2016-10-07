New implementation of messages
==============================

This is a complete reimplementation the messages and parser.


Goals
-----

* cleaner implementation
* drop-in replacement
* easier to extend and work with


Messages as Dictionaries
------------------------

Instead of converting directly between messages and bytes there is now
a middle step: a dictionary::

    {'type': 'note_on', 'note': 60, 'velocity': 120, 'time': 1.0}

The `Message` object is just a thin wrapper around this dictionary.

All the code doing encoding and decoding of MIDI bytes work on
dictionaries and now longer needs to know about `Message`
objects. This make the code more modular and easier to reason about,
test and change.

The overloaded `messages.py` has been broken up into `defs.py`,
`check.py`, `msg.py` and `strings.py`.


Messages are Iterable
---------------------

You can now iterate over the bytes in a message. This allows you to do
things like:

.. code-block:: python

    >>> m = Message('note_on')
    >>> m
    <message note_on channel=0 note=0 velocity=64 time=0>

    >>> bytes(m)
    b'\x90\x00@'

    >>> bytearray(m)
    bytearray(b'\x90\x00@')

    >>> list(m)
    [144, 0, 64]

    >>> tuple(m)
    (144, 0, 64)

Which corresponds very nicely with:

.. code-block:: python

    >>> str(m)
    'note_on channel=0 note=0 velocity=64 time=0'

The old `msg.bin()`, `msg.bytes()` (which confusingly returns a list)
and `msg.bytearray()` are still kept around for old programs. (Should
they?)


Converting from Bytes and Strings
---------------------------------

Now you can also convert the other way without `parse()` or
`parse_string()`:

.. code-block:: python

    >>> Message.from_str('note_on channel=0 note=0 velocity=64 time=0')
    <message note_on channel=0 note=0 velocity=64 time=0>

    >>> Message.from_bytes(b'\x90\x00@')
    <message note_on channel=0 note=0 velocity=64 time=0>

    >>> Message.from_bytes([144, 0, 64])
    <message note_on channel=0 note=0 velocity=64 time=0>

This is nicely orthogonal.


Backward Incompatible Changes
-----------------------------

* messages are immutable (easy to add mutability though)
* time is included in comparisons (probably worth it)
* Python 3 only (for now)
* sysex data are bytes objects (b''). This will probably cause problems.


Status
------

* feature complete but needs some work
* doesn't pass all tests yet
* needs more doc strings
* MIDI files are broken (since they require build_message() and get_spec())
* meta messages are broken
* more checks are needed (currently doesn't check for unknown attribute names)
* some more thought needs to be put into terminology (`msgdict` for example)
* the content of `defs.py` needs some restructuring and renaming
