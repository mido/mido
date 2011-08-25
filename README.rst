MIDI library for Python
========================

MIDI messages are immutable objects::

    >>> import midi
    >>> msg = midi.msg.note_on(note=60, vel=100)
    >>> msg
    note_on(time=0, chan=0, note=60, vel=100)
    >>> msg.note
    60
    >>> msg.note = 20
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "midi/msg.py", line 184, in __setattr__
        raise ValueError('MIDI message object is immutable')
    ValueError: MIDI message object is immutable

New messages are created by copying an existing message:

    >>> msg.copy(chan=1)
    note_on(time=0, chan=1, note=60, vel=100)

Sysex messages are supported::

    >>> midi.msg.sysex(vendor=22, data=[1, 4, 2, 5, 6, 7])
    sysex(time=0, vendor=22, data=(1, 4, 2, 5, 6, 7))

Illegal values will be detected::

    >>> midi.msg.note_on(note='BOO!')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "midi/msg.py", line 159, in copy
        new._update(kw)
      File "midi/msg.py", line 132, in _update
        assert_data(value)
      File "midi/asserts.py", line 39, in assert_data
        raise ValueError('MIDI data byte must an in range [0 .. 127] (was %s)' % repr(val))
    ValueError: MIDI data byte must an in range [0 .. 127] (was 'BOO!')


Plans
------

I will write a general purpose MIDI parser which can be used for
parsing data from any source by feeding it bytes and fetching messages
as they become available.

I have also almost finished writing a wrapper for PortMidi, which will
provide MIDI I/O on Linux, Mac OS X, Windows and possibly other
platforms.


Design goals
-------------

  - DRY
  - MIDI messages should be immutable
  - MIDI messages should be pure data objects, with no methods other than
    __init__(), __call__(), __repr__(), __str__() and rich comparison
    operators. Utility functions will be used instead (midi.is_chanmsg() etc.)
  - the contructor must check if values are of the correct type and within range,
    so they can safely be serialized
  - serialized versions of the message is available in .bytes and .bin. One is
    an array of byte values as integers, the other is a byte array. I may change
    the names.
  - the Sysex message will have its data bytes stored as a tuple of integers



Todo
-----

   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)
   - include useful lookup tables and functions for common things like
     scales and controller types
   - read and write MIDI files?
   - support rich comparisons (easy with self.bytes and self.bin)


Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT
