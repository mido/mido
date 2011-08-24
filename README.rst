MIDI library for Python
========================

Works in Python 2 and Python 3.

MIDI messages are immutable objects::

    >>> import midi
    >>> msg = midi.note_on(note=60)
    >>> msg
    note_on(time=0, chan=0, note=60, vel=127)
    >>> msg.note
    60
    >>> msg.bytes
    (144, 60, 127)
    >>> msg.bin
    b'\x90<\x7f'

The immutability is not enforced (yet), so you can screw things up
by doing::

    >>> doomed_msg = midi.note_on()
    >>> doomed_msg.note = 'Mwuahahahaha!'
    >>> doomed_msg
    note_on(time=0, chan=0, note=Mwuahahahaha!, vel=127)
    >>> del doomed_msg.bytes
    >>> doomed_msg.bytes
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: note_on instance has no attribute 'bytes'

This may cause all sorts of problems later on, and it is easy to do
by mistake, so I am planning to fix it.

A modified clone can be created by calling ``msg.copy``::

    >>> msg.copy(note=20)
    note_on(time=0, chan=0, note=20, vel=127)

Sysex messages are supported::

    >>> midi.sysex(vendor=22, data=[1, 4, 2, 5, 6, 7])
    sysex(time=0, vendor=22, data=(1, 4, 2, 5, 6, 7))

Only note_on, note_off and sysex are implemented so far, but I plan to
implement all message types.

Illegal values will be detected::

    >>> midi.note_on(note='BOO!')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/olemb/src/git/midi/midi.py", line 86, in __init__
        [assert_data_byte(b) for b in [chan, note, vel]]
      File "/home/olemb/src/git/midi/midi.py", line 86, in <listcomp>
        [assert_data_byte(b) for b in [chan, note, vel]]
      File "/home/olemb/src/git/midi/midi.py", line 37, in assert_data_byte
        raise ValueError('MIDI data byte must an integer >= 0 and <= 127 (was %r)' % value)
    ValueError: MIDI data byte must an integer >= 0 and <= 127 (was 'BOO!')
    
    >>> midi.note_on()
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/olemb/src/git/midi/midi.py", line 85, in __init__
        assert_time_value(time)
      File "/home/olemb/src/git/midi/midi.py", line 44, in assert_time_value
        raise ValueError('MIDI time value must be a number >= 0 (was %r)' % time)
    ValueError: MIDI time value must be a number >= 0 (was [1, 2, 3])

There is no support yet for I/O, but if you still have OSS MIDI on
your system, you can do this:

    >>> dev = open('/dev/midi', 'wb')
    >>> dev.write(midi.note_on(note=60).bin)

I will write a general purpose MIDI parser which can be used for
parsing data from any source by feeding it bytes and fetching messages
as they become available. This can be plugged into any existing MIDI
library like PortMIDI or Core MIDI, or it can be used to write a MIDI
file class.

For now, this is mainly an excercise in API design and a way for me to
play around with interesting Python data types, but if it turns out
well, I will use it to write a patch librarian for my synths, and
perhaps some other toys.

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

   - MIDI channels are numbered 1-16 in user interfaces, but are
     numbered 0-15 in the protocol. Which version should midi.py show?
   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)
   - include useful lookup tables and functions for common things like
     scales and controller types
   - read and write MIDI files?
   - serialize messages to text files
   - reformat midi.txt to make it more useful (hex values in addition to binary)
   - support rich comparisons (easy with self.bytes and self.bin)


Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT
