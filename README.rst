ProtoMIDI - a MIDI library for Python
======================================

Works in Python 2 and 3.

::

    >>> from protomidi.msg import *
    >>> msg = note_on(note=60, velocity=100)
    >>> msg
    note_on(time=0, channel=0, note=60, velocity=100)
    >>> msg.type
    'note_on'
    >>> msg.note
    60

MIDI messages are immutable::

    >>> msg.note = 20
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "midi/msg.py", line 184, in __setattr__
        raise ValueError('MIDI message object is immutable')
    ValueError: MIDI messages are immutable

New messages are created by calling an existing object as
a function, passing keyword arguments for values you want to
change::

    >>> msg(channel=1)
    note_on(time=0, channel=1, note=60, velocity=100)

Sysex messages are supported::

    >>> sysex(vendor=22, data=[1, 4, 2, 5, 6, 7])
    sysex(time=0, vendor=22, data=(1, 4, 2, 5, 6, 7))

Illegal values will be detected::

    >>> note_on(note='BOO!')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "midi/msg.py", line 159, in copy
        new._update(kw)
      File "midi/msg.py", line 132, in _update
        assert_data(value)
      File "midi/asserts.py", line 39, in assert_data
        raise ValueError('MIDI data byte must an in range [0 .. 127] (was %s)' % repr(val))
    ValueError: MIDI data byte must an in range [0 .. 127] (was 'BOO!')

(Todo: regenerate this:)

Here is a list of all MIDI messages and their default values (subject
to change, as the API is not completely stable yet)::

    note_off(time=0, chan=0, note=0, vel=0)
    note_on(time=0, chan=0, note=0, vel=0)
    polytouch(time=0, chan=0, note=0, value=0)
    control(time=0, chan=0, number=0, value=0)
    program(time=0, chan=0, program=0)
    aftertouch(time=0, chan=0, value=0)
    pitchwheel(time=0, chan=0, value=0)
    sysex(time=0, vendor=0, data=())
    undefined_f1(time=0)
    songpos(time=0, pos=0)
    song(time=0, song=0)
    undefined_f4(time=0)
    undefined_f5(time=0)
    tune_request(time=0)
    sysex_end(time=0)
    clock(time=0)
    undefined_f9(time=0)
    start(time=0)
    continue_(time=0)
    stop(time=0)
    undefined_fd(time=0)
    active_sensing(time=0)
    reset(time=0)

``time`` is a number that can be used to keep track of of when the
message was received, how long to delay before sending it, and such
things.


Plans
------

I have also nearly finished writing a wrapper for PortMidi, which will
provide MIDI I/O on Linux, Mac OS X and Windows.

I will write thorough documentation on both the use of the library,
its internals and the MIDI protocol.


Todo
-----

   - write docs
   - implement serialization of messages
   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)
   - include useful lookup tables and functions for common things like
     controller types
   - read and write MIDI files?
   - implement comparison (== and !=), but not < and > (they don't make sense here)
   - document the implementation of messages in msg.py.
     (the prototyping object model, how attributes are made read only etc.)
     This should be in docs/, not in in the msg.py.
   - write a short introduction on the MIDI protocol, using this library
     for examples
   - support Python 3

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

Credits: Initialization code in portaudio.py by Grant Yoshida, borrowed from his module portmidizero.
