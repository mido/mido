ProtoMIDI - a MIDI library for Python
======================================

ProtoMIDI aims to make it easy to write Python programs to manipulate
MIDI data, such as sequencers, patch editors or just experimental
scripts. A small example (API may change)::

    import time
    import random
    from protomidi.msg import *
    from protomidi.portmidi import Output

    # Play random notes
    out = Output()
    while 1:
        note = random.randrange(128)

        out.send(note_on(note=note, velocity=70))
	time.sleep(0.25)
	out.send(note_off(note=note))

MIDI messages are immutable objects. A new message can be created by
calling an existing message and overriding some of its values::

    >>> from protomidi.msg import note_on
    >>> msg = note_on(note=22, velocity=100)
    >>> msg
    note_on(channel=0, note=22, velocity=100)
    >>> msg(note=60)
    note_on(channel=0, note=60, velocity=100)


Planned features
----------------

(All implemented, but with a lot of testing and fine polishing remaining.)

    - abstract immutable MIDI message objects that are
      easy to work with
    - support for all MIDI message types (including sysex)
    - parser / serializer (seralizes to bytearray or bytes)
    - Input and Output classes for communicating with other MIDI programs or devices (portmidi)


Status
------

The library is under development. The code may not be stable and the
API may change.


Known bugs
----------

  - Sysex input is broken, and it seems like the fault lies in portmidi itself. (I've checked
    the output of amidi against the raw portmidi event.message, and portmidi starts off fine
    and then goes into periods of nonsense values.) Next step: see if it works on OS X. Then
    off to dig deeper into portmidi to see what's going on.

  - portmidi.Output.send() sometimes segfaults in Linux. Fortunately, if it doesn't
    segfault the first time you call it, it will never segfault again. So if this happens,
    just restard the program.


Requirements
------------

ProtoMIDI works Python 2.7 and 3.2 (may work with older versions, but I haven't tested this.)

Requires portmidi shared library if you want to use the I/O classes.

I'm using Ubuntu 11.4 and Mac OS Lion, but it should run wherever
there you have Python and a portmidi shared library.


Todo
-----

   - show sysex bytes in hexadecimal? (in __repr__())

   - write function (or functions) to search for MIDI devices (get_input(), get_device(name='UM-1', input=1),
     etc.)

   - figure out where to call portmidi.initialize()

   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)

   - include useful lookup tables or message attributes for common things like
     controller types

   - handle devices that send note_on(velocity=0) instead of note_off() (flag
     for portmidi.Input()?) Perhaps make it an option so you can choose the one you prefer,
     and any data will be converted to that format.

   - attach some kind of time value to messages returned from Input.recv()? (Or should 
     the user pass a time function?)

   - do we actually need to set the timer in Input() and Output()?

   - show time value in __repr__()? Also, does assert_time handle time=None?


   - write docs

   - document the implementation of messages in msg.py.
     (the prototyping object model, how attributes are made read only etc.)
     This should be in docs/, not in in the msg.py.

   - write a short introduction on the MIDI protocol, using this library
     for examples


Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

Credits: The Portmidi wrapper is based on Portmidizero by Grant Yoshida.
