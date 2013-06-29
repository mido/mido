Mido - Object Oriented MIDI for Python
=======================================

Mido allows you to work with MIDI messages as Python objects:

.. code:: python

    >>> import mido
    >>> msg = mido.new('note_on', note=60, velocity=64)
    >>> msg
    mido.Message('note_on', channel=0, note=60, velocity=64, time=0)
    >>> str(msg)
    'note_on channel=0 note=60 velocity=64'
    >>> msg.type
    'note_on'
    >>> msg.channel = 6
    >>> msg.note = 19
    >>> msg2 = msg.copy(channel=9, velocity=127)
    >>> msg == msg2
    False

System Exclusive messages:

.. code:: python

    >>> s = mido.new('sysex', data=[1, 2])
    >>> s.hex()
    'F0 01 02 F7'
    >>> s.data = (i for i in range(5))
    >>> s.hex()
    'F0 00 01 02 03 04 F7'

Sending and receiving messages via PortMidi:

.. code:: python

    >>> inport = mido.input()
    >>> outport = mido.output()
    >>> for msg in inport:
    ...     outport.send(msg)

Ports can opened by name:

.. code:: python

    >>> mido.input_names()
    ['Midi Through Port-0', 'SH-201']
    >>> mido.input('SH-201')
    <open input port 'SH-201' (ALSA)>
    
Since Mido uses duck typing, you can add new port types and backends
without involving Mido at all. All you need are objects that support
the functionality you want to use. For example:

.. code:: python

    import mido

    class PrintPort:
        def send(self, message):
            print(message)

    with mido.input(), LogPort() as inport, outport:
        for message in inport:
            outport.send(message)

or::

    import mido
    import rtmido  # fictional wrapper for RtMido

    with rtmido.output() as port:
        port.send(mido.new('pitchbend', channel=3, pitch=842))
        ...


Status
-------

Mido is not quite ready for a formal release, but it's close. All of
the basic functionality is in place, and the API is unlikely to change
much from this point. What remains is to write thorough documentation
and to add more unit tests.

I am aiming for a release sometime in July 2013.


License
--------

Released under the MIT license.


Requirements
-------------

Mido uses `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ for I/O. The
wrapper module is written using ctypes, so no compilation is
required. All you need is portmidi.so/dll installed on your system.

PortMidi is loaded on demand when you open a port or call one of the
I/O functions like `mido.input_names()`.

PortMidi is only required if you want to use message ports. The
messages themselves work fine without it.

Developed for Python 2.7 and 3.2. Tested on Ubuntu 13.04 and Mac OS X
10.7.5, but should run on whatever system PortMidi is ported to.


Installing
-----------

In the Linux / OS X terminal::

    $ sudo python2 setup.py install

or::

    $ sudo python2 setup.py install

Installing libportmidi in Ubuntu::

    $ sudo apt-get install libportmidi-dev


More About MIDI
----------------

http://www.midi.org/


Known Bugs
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


Future Plans
-------------

   - include useful lookup tables or message attributes for common
     things like controller types

   - fix extras/joystick.py

   - use libportmidi-dev or libportmidi0?


Mido is short for MIDi Objects (or Musical Instrument Digital
Objects). It is pronounced with i and in "little" and o as in
"object", or in Japanese: ミド.

Latest version of the code: http://github.com/olemb/mido/ .

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

The PortMidi wrapper is based on portmidizero by Grant Yoshida.

Thanks to tialpoy on Reddit for extensive code review and helpful
suggestions.
