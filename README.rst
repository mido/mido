Mido - Object oriented MIDI for Python
=======================================

Mido allows you to work with MIDI messages as Python objects:

.. code:: python

    >>> import mido
    >>> msg = mido.new('note_on', note=60, velocity=64)
    >>> msg
    mido.Message('note_on', channel=0, note=60, velocity=64, time=0)
    >>> msg.type
    'note_on'
    >>> msg.channel = 6
    >>> msg.note = 19
    >>> msg2 = msg.copy(channel=9, velocity=127)
    >>> msg == msg2
    False

Sysex messages:

.. code:: python

    >>> s = mido.new('sysex', data=[1, 2])
    >>> s.hex()
    'F0 01 02 F7'
    >>> s.data = (i for i in range(5))
    >>> s.hex()
    'F0 00 01 02 03 04 F7'

Sending and receiving messages via PortMidi:

.. code:: python

    >>> from mido.portmidi import Input, Output
    >>> outport = Output()
    >>> outport.send(msg)
    >>> inport = Input()
    >>> for msg in inport:
    >>>     print(msg)

Ports can opened by name:

.. code:: python

    >>> from mido.portmidi import get_input_names
    >>> get_input_names()
    ['Midi Through Port-0', 'SH-201']
    >>> Input()  # Open default port
    <open input 'Midi Through Port-0' (ALSA)>'
    >>> Input('SH-201')
    <open input 'SH-201' (ALSA)>'
    

Status
-------

Mido is not quite ready for production, but it's close. All of basic
functionality is in place, and the API is unlikely to change much from
this point.

What remains is mostly documentation. Also, the code needs a bit more
work, and many more test cases have to be written.


License
--------

Released under the MIT license.


Requirements
-------------

Mido uses PortMidi for I/O. The wrapper module is written using
ctypes, so no compilation is required. All you need is portmidi.so/dll
installed on your system.

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
-----------

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

  - if close() is in the __exit__() method of an output port, or
    context.closing() is used on the port, an exception is raised
    saying "send() called on closed port". This needs to be figured
    out.


Todo
-----

   - make the last few modifications to the basic API

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

   - base classes for input and output ports to make it easier to
     implement new backends?

   - __enter__ / __exit__ for ports? (with Output() as port: port.send(msg))

   - fix extras/joystick.py

   - use libportmidi-dev or libportmidi0?


Mido is short for MIDi Objects (or Musical Instrument Digital Objects).

Latest version of the code: http://github.com/olemb/mido/ .

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

The PortMidi wrapper is based on portmidizero by Grant Yoshida.
