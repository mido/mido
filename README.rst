Modo - a MIDI library for Python
=================================

Mido is a Python library for sending, receiving and processing MIDI
messages. There are currently backends for PortMIDI (tested with Linux
and Mac OS X, but may also work on Windows) and amidi (the Linux
utility program).

Mido works with Python 2 and 3. The PortMIDI backend is written in
Python and requires no compilation.

License: MIT


Examples
---------

Creating and modifying a message::

    >>> import mido
    >>> msg = mido.new('note_on', note=60, velocity=64)
    >>> msg.channel = 7
    >>> msg.note=127
    >>> msg
    mido.Message('note_on', channel=7, note=127, velocity=64, time=0)

Sending a message via PortMIDI::

    >>> from mido.portmidi import Output
    >>> out = Output('SH-201')
    >>> out.send(msg)

Copying a message::

    >>> msg.copy(note=23, time=22)
    mido.Message('note_on', channel=7, note=23, velocity=64, time=22)

More examples at the bottom.


Requirements
------------

Mido works with Python 2.7 and 3.2 (may work with older versions, but
I haven't tested this.)

Requires portmidi shared library if you want to use the I/O classes.

I'm using Ubuntu 13.04 and Mac OS X 10.7.5, but it should run wherever
there you have Python and a portmidi shared library.


Known bugs
----------

  - on OS X, portmidi sometimes hangs for a couple of seconds while
    initializing.

  - in Linux, I sometimes experience short lags, as if messages
    are bunched up and then released again. I don't know what causes this,
    but I suspect that another process is sometimes stealing the CPU
    for long enough for this to happen. (Could it be garbage collection?
    I doubt it, but I won't rule it out yet.)


Todo
-----

   - implement blocking or callbacks for Input ports

   - include some kind of event based scheduler?

   - include useful lookup tables or message attributes for common
     things like controller types

   - handle devices that send note_on(velocity=0) instead of
     note_off() (flag for portmidi.Input()?) Perhaps make it an option
     so you can choose the one you prefer, and any data will be
     converted to that format.

More in the TODO file.


More examples
--------------

One of these::

    $ sudo python2 setup.py install
    $ sudo python3 setup.py install


Default values for everything is 0 (and () for sysex data)::

    >>> mido.new('note_on')
    mido.Message('note_on', channel=0, note=0, velocity=0, time=0)
    >>> mido.new('sysex')
    mido.Message('sysex', data=(), time=0)

Encoding a message::

    >>> msg.bytes()
    [151, 60, 64]
    >>> msg.hex()
    '97 3C 40'
    >>> msg.bin()
    bytearray(b'\x97<@')

Sysex messages::

    >>> s = mido.new('sysex', data=[1, 2])
    >>> s.hex()
    'F0 01 02 F7'
    >>> s.data = (i for i in range(5))
    >>> s.data
    (0, 1, 2, 3, 4)
    >>> s.hex()
    'F0 00 01 02 03 04 F7'

(Note that sysex messages contain the sysex_end byte (0xF7), so a
separate 'sysex_end' message is not necessary.)


Time
-----

The time attribute can be used for time annotations. Mido doesn't care
what you use it for, as long as it's a valid number. Examples::

    >>> msg.time = 183
    >>> msg.time = 220.84

The time attribute will not affect comparisons::

    >>> msg2 = msg.copy(time=20000)
    >>> msg == msg2
    True

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

: The Portmidi wrapper is based on Portmidizero by Grant Yoshida.
