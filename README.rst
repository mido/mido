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

Sending a message via PortMIDI:

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

The messages and PortMIDI Input and Output classes are fully implemented,
and their API is unlikely to change. Some changes will be made to the Parser
class to make its methods a little more consistent and streamlined, and
the get_input/output_port() will probably be replaced with something that
also returns the state of the port (such as whether it is open or not).



License
--------

Released under the MIT license.


Requirements
-------------

Mido uses PortMIDI for I/O. A wrapper module is included, so all you
need is is portmidi.so/dll installed on your system. PortMIDI is only
required for I/O. The messages will work fine without it.

Tested with Python 2.7 and 3.3. (3.2 should be OK. Older versions may
or may not work.)

Runs on Linux 13.04 and Mac OS X 10.7.5. May also work on Windows.


Installing
-----------

In the Linux / OS X terminal::

    $ sudo python2 setup.py install

or::

    $ sudo python2 setup.py install


Known bugs
----------

  - on OS X, portmidi sometimes hangs for a couple of seconds while
    initializing.

  - in Linux, I sometimes experience short lags, as if messages
    are bunched up and then released again. I don't know what causes this,
    but I suspect that another process is sometimes stealing the CPU
    for long enough for this to happen. (Could it be garbage collection?
    I doubt it, but I won't rule it out yet.)

  - libportmidi prints out error messages instead of returns err and
    setting the error message string. This is most likely a bug in
    portmidi but it trickles up.
    
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


More examples
--------------

Receiving a message:

.. code:: python

    >>> from mido.portmidi import Input
    >>> input = Input()
    >>> msg = input.recv()

Non-blocking receive:

.. code:: python

    >>> if input.poll():
    >>>     msg = input.recv()

Inputs and outputs take an optional port name. This is name of the
ALSA / CoreMIDI device to use:

.. code:: python

   >>> out = Output('SH-201')

Available port names can be listed (but the exact API may change):

   >>> import mido.portmidi as pm
   >>> print(pm.get_input_names())
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
    >>> mido.parseall([0x80, 60, 64, 0x90, 60, 64])
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


Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

The Portmidi wrapper is based on Portmidizero by Grant Yoshida.
