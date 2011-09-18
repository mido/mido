.. ProtoMIDI documentation master file, created by
   sphinx-quickstart on Thu Aug 25 23:38:39 2011.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ProtoMIDI - a MIDI library for Python
=====================================

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

The library is under development. The code may not be stable and the
API may change.


Requirements
------------

ProtoMIDI will work with Python 2 and 3 (todo: be more specific).

If you want to use the Input and Output classes, you will also need
the portmidi shared library.

To intall portmidi in Ubuntu (and possibly Debian)::

    sudo apt-get install libportmidi0

To install portmidi on OS X (using macports)::

    sudo port install portmidi
    export LD_LIBRARY_PATH=/opt/local/lib

(The last line should probably be added to .profile or some other
file. I'm not sure if this is a good way to add libraries to the path,
but it will have to do for now.)


MIDI messages
-------------

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

Messages can be serialized to bytearrays so they can be
sent or written to MIDI files::

    >>> from protomidi import serialize
    >>> serialize(sysex(data=[1, 2, 3]))
    bytearray(b'\xf0\x00\x01\x02\x03\xf7')

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



Contents:

.. toctree::
   :maxdepth: 2

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

