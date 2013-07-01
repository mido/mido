Mido - MIDI Objects for Python
===============================

Requires Python 2.7 or 3.2. Runs on Ubuntu and Mac OS X. May also run
on other systems.

License: MIT

Mido is a library for working with MIDI messages and ports. It's
designed to be as straight forward and Pythonic as possible.

.. code:: python

    >>> import mido
    >>> 
    >>> msg = mido.new('note_on', note=60, velocity=100)
    >>> msg.type
    'note_on'
    >>> msg.channel = 2
    >>> msg.copy(note=62, velocity=73)
    <note_on message channel=2, note=62, velocity=73, time=0>

    >>> msg = mido.new('sysex', data=[byte for byte in range(5)])
    >>> msg.data
    (0, 1, 2, 3, 4)
    >>> msg.data = [ord(char) for char in 'Hello MIDI!']
    >>> msg.hex()
    'F0 48 65 6C 6C 6F 20 4D 49 44 49 21 F7'
    >>> msg(sysex)
    13

Messages can be sent and received on ports:

.. code:: python

    default_input = mido.input()
    output = mido.output('SH-201')

    for message in default_input:
        output.send(message)

Non-blocking `receive()` is possible with `pending()`:

.. code:: python

    if input.pending() > 0
        message = input.receive()

To use ports, you need to have `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_ installed on
your system.

When you assign to attributes or pass keyword arguments, they are checked
for each possible way they could be invalid:

.. code:: python

    >>> msg = mido.new('pitchwheel', banana=1)
    ValueError: 'banana' is an invalid keyword argument for this message type
    >>> msg = mido.new('pitchwheel', pitch=100)
    >>> msg.pitch = 1235892384
    ValueError: pitchwheel value must be in range -8192..8191
    >>> msg.pitch = 'Banana!'
    TypeError: pichwheel value must be an integer

This ensures that you always have a valid message.


Status
-------

Mido is not quite ready for a formal release, but it's close. All of
the basic functionality is in place, and the API is unlikely to change
much from this point. What remains is to write thorough documentation
and to add more unit tests.

I am aiming for a release sometime in July 2013.


Requirements
-------------

If you want to use message ports, you need to install `PortMidi
<http://sourceforge.net/p/portmedia/wiki/portmidi/>`_. Mido loads
libportmidi.so / .dll on demand when you open a port or call one of
the I/O functions like `mido.input_names()`. The wrapper module is
written with ctypes and requires no compilation.


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

  - in interactive mode, this happens (but only in interactive mode)
    (edit: this is because the input is still bound to _):

.. code:: python

    >>> import mido
    >>> mido
    >>> mido.input()
    <open input port 'Midi Through Port-0' (ALSA)>
    >>> mido.input()
    PortMidi call failed...
      PortMidi: `Invalid device ID'
    type ENTER...
    
    # In a script, it works fine.
    import mido
    
    mido.input()  # __del__() is called here
    mido.input()  # and here

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


Mido is short for MIDi Objects (or Musical Instrument Digital
Objects). It is pronounced with i and in "little" and o as in
"object", or in Japanese: ミド.

Latest version of the code: http://github.com/olemb/mido/ .

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

The PortMidi wrapper is based on portmidizero by Grant Yoshida.

Thanks to tialpoy on Reddit for extensive code review and helpful
suggestions.
