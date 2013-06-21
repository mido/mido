Modo - a MIDI library for Python
=================================

Modo is a Python library for sending, receiving and processing MIDI messages.
(There is no support for MIDI files. Maybe in the future.)

Modo currently has backends for PortMIDI (tested with Linux and OSX)
and amidi (the Linux utility program).


Example 1: play with messages
------------------------------

(This doesn't require PortMIDI.)

    >>> from modo.msg import *
    >>> pc = program_change(channel=3, program=9)
    >>> pc
    Message('program_change', channel=3, program=9, time=0)
    >>> pc.channel
    3
    >>> pc.channel = 6
    >>> pc


Example 2: send a message
--------------------------

    >>> from modo.msg import *
    >>> from modo.portmidi import Output
    >>> 
    >>> output = Output()  # Default output
    >>> pc = program_change(channel=0, program=9)
    >>> output.send(pc)

Sending to a specific output:

    >>> output = Output()


Requirements
------------

Modo works with Python 2.7 and 3.2 (may work with older versions, but
I haven't tested this.)

Requires portmidi shared library if you want to use the I/O classes.

I'm using Ubuntu 11.4 and Mac OS Lion, but it should run wherever
there you have Python and a portmidi shared library.


Working with MIDI ports
------------------------

Print all messages received from the SH-201 synthesizer.

    import time
    from modo.portmidi import Input, Output, get_devices

    inport = Input('SH-201 MIDI 1')
    
    while 1:
        for msg in inport:
            print(msg)

        # We can't block, so unfortunately
        # we have to do this instead.
        time.sleep(0.01)


Message factory functions
--------------------------

    note_off(channel=0, note=0, velocity=0, time=0)

    note_on(channel=0, note=0, velocity=0, time=0)

    polytouch(channel=0, note=0, value=0, time=0)

    control_change(channel=0, control=0, value=0, time=0)

    program_change(channel=0, program=0, time=0)

    aftertouch(channel=0, value=0, time=0)

    pitchwheel(channel=0, value=0, time=0)

    sysex(data=(), time=0)

    undefined_f1(time=0)

    songpos(pos=0, time=0)

    song(song=0, time=0)

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


Known bugs
----------

  - on OS X, portmidi sometimes hangs for a couple of seconds while
    initializing.

  - default input/output doesn't work in Linux. Adding a default
    input/output in the alsa config will probably help. (This is not
    really a bug, but just how ALSA works.)

  - in Linux, I am experiencing occasional short lags, as if messages
    are bunched up and then released again. I don't know what causes this,
    but I suspect that another process is sometimes stealing the CPU
    for long enough for this to happen. (Could it be garbage collection?
    I doubt it, but I won't rule it out yet.)




Todo
-----

   - show sysex bytes in hexadecimal? (in __repr__())

   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)

   - include useful lookup tables or message attributes for common things like
     controller types

   - handle devices that send note_on(velocity=0) instead of note_off() (flag
     for portmidi.Input()?) Perhaps make it an option so you can choose the one you prefer,
     and any data will be converted to that format.


Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT

Credits: The Portmidi wrapper is based on Portmidizero by Grant Yoshida.
