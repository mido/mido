Mido - Object oriented MIDI for Python
=======================================

Mido allows you to work with MIDI messages as Python objects:

.. code:: python

    >>> import mido
    >>> msg = mido.new('note_on', note=60, velocity=64)
    >>> msg.channel
    0
    >>> msg.type
    'note_on'
    >>> msg.channel = 7
    >>> msg.note = 127
    >>> msg
    mido.Message('note_on', channel=7, note=127, velocity=64, time=0)

Sending a message via PortMidi:

.. code:: python

    >>> from mido.portmidi import Output
    >>> out = Output()
    >>> out.send(msg)

Copying a message:

.. code:: python

    >>> msg.copy(note=23, time=22)
    mido.Message('note_on', channel=7, note=23, velocity=64, time=22)


Status
-------

Mido is not quite ready for production, but it's close. I hope to get
some feedback before I finalize the API and release the first
official version.

The messages and PortMidi Input and Output classes are fully
implemented, and their API is unlikely to change much. Some changes
will be made to the Parser class to make its methods a little more
consistent and streamlined.

Some of the code raises the wrong type of exceptions. This will have
to be fixed.



License
--------

Released under the MIT license.


Requirements
-------------

Mido uses PortMidi for I/O. The wrapper module is written using
ctypes, so no compilationis is required. All you need is
portmidi.so/dll installed on your system.

PortMidi is only required if you want to use message ports. The
messages will work fine without it.

Developed for Python 2.7 and 3.3. (3.2 should be OK. Older versions
may or may not work.)

Runs on Linux 13.04 and Mac OS X 10.7.5. May also work on Windows.


Installing
-----------

In the Linux / OS X terminal::

    $ sudo python2 setup.py install

or::

    $ sudo python2 setup.py install


Known bugs
----------

  - on OS X, PortMidi sometimes hangs for a couple of seconds while
    initializing.

  - in Linux, I sometimes experience short lags, as if messages
    are bunched up and then released again. This is probably a PortMidi
    problem.

  - libportmidi prints out error messages instead of returning err and
    setting the error message string. This is most likely a bug in
    PortMidi but it trickles up.
    
  - there is an obscure bug involving the OS X application Midi Keys.
    See tmp/segfault.py


Todo
-----

   - make the last few modifications to the basic API

   - add an __iter__() method to ports. It is unclear whether this should
     block or not.

   - include a callback mechanism and maybe some kind of event based
     system. This can be built as a library that on top of port and message
     objects.
   
   - include useful lookup tables or message attributes for common
     things like controller types

   - handle devices that send note_on(velocity=0) instead of
     note_off() (flag for portmidi.Input()?) Perhaps make it an option
     so you can choose the one you prefer, and any data will be
     converted to that format.
     
   - raise more sensible exceptions

   - there is currently no way of telling if am I/O device is opened
     or not. portmidi.get_input/output_names() and .get_output_names()
     should probably return name/isopened instead of just a name.

   - base classes for input and output ports to make it easier to
     implement new backends?

   - handle unicode port names

   - add backened attr to ports? (port.backend == 'portmidi')

   - add comparison for messages (should time be compared?)

   - AttributeError / SomethingError for msg.tuba = 1 vs. msg.copy(tuba=1)

   - __enter__ / __exit__ for ports? (with Output() as port: port.send(msg))

   - fix extras/joystick.py

   - use libportmidi-dev or libportmidi0?



More examples
--------------

Receiving a message:

.. code:: python

    >>> from mido.portmidi import Input
    >>> port = Input()
    >>> msg = port.receive()

Non-blocking receive:

.. code:: python

    >>> if port.poll():
    ...     msg = input.receive()
    ...     print(msg)

Inputs and outputs take an optional port name, which is name of the
ALSA / CoreMIDI device to use:

.. code:: python

   >>> out = Output('SH-201')

Available port names can be listed (but the exact API may change):

   >>> from portmidi import get_input_names()
   >>> get_input_names()
   ['Midi Through Port-0', 'SH-201 MIDI 1']

Encoding messages:

.. code:: python

    >>> msg.bytes()
    [151, 60, 64]
    >>> msg.hex()
    '97 3C 40'
    >>> msg.bin()
    bytearray(b'\x97<@')

Parsing:

.. code:: python

    >>> mido.parse([0x90, 60, 64])
    mido.Message('note_on', channel=0, note=60, velocity=64, time=0)
    >>> mido.parse_all([0x80, 60, 64, 0x90, 60, 64])
    [mido.Message('note_off', channel=0, note=60, velocity=64, time=0),
    mido.Message('note_on', channel=0, note=60, velocity=64, time=0)]
    >>> mido.parse(b'\x80Ab')
    mido.Message('note_off', channel=0, note=65, velocity=98, time=0)

msg.bytes() and mido.parse() can be used to send and receive messages
via libraries which use byte based I/O, such as rtMidi.

Sysex messages:

.. code:: python

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

Default values for everything is 0 (and () for sysex data):

.. code:: python

    >>> mido.new('note_on')
    mido.Message('note_on', channel=0, note=0, velocity=0, time=0)
    >>> mido.new('sysex')
    mido.Message('sysex', data=(), time=0)


Time
-----

The time attribute can be used for time annotations. Mido doesn't care
what you use it for, as long as it's a valid number. Examples:

.. code:: python

    >>> msg.time = 183
    >>> msg.time = 220.84

The time attribute will not affect comparisons:

.. code:: python

    >>> msg2 = msg.copy(time=20000)
    >>> msg == msg2
    True

More documentation is planned.


Mido is short for MIDi Objects (or Musical Instrument Digital Objects).

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

The PortMidi wrapper is based on Portmidizero by Grant Yoshida.
