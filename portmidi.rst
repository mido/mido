portmidi.py - a pure Python wrapper for PortMidi with a pythonic API
=====================================================================

Status: Drafting API.

::

    import midi
    import time

    with midi.portmidi.context():
        out = midi.portmidi.Output()
        out.send(midi.msg.note_on(note=60, vel=127))
        time.sleep(0.5)
        out.send(midi.msg.note_off(note=60)

Use ctypes.

Todo: include .so files for various operating systems? (For convenience.)

PortMidi API: http://portmedia.sourceforge.net/portmidi/doxygen/portmidi_8h-source.html


Another implentation: http://code.google.com/p/pyanist/source/browse/trunk/lib/portmidizero/portmidizero.py?spec=svn2&r=2


