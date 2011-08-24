MIDI library for Python
========================

    >>> import time
    >>> import midi
    >>> out = midi.MidiOut('/dev/midi')
    >>> channel = 2  # note: midi channel 3
    >>> # 60=middle C, 67=G, 72=C
    >>> for note in [60, 67, 72]:
    ...    out.send(midi.note_on(channel=channel, note=note))
    ...    time.sleep(0.1)
    ...    out.send(midi.note_off(channel=channel, note=note))

The library uses OSS MIDI ('/dev/midi', '/dev/midi1' etc.), which is
pretty hard to come by these days.  I may add support for PortMIDI
(http://portmedia.sourceforge.net/) and/or Core MIDI. It should be as
easy as writing new midi.MidiIn and midi.MidiOut classes (I hope).

I am currently attempting to rewrite midi.py, to get rid of all the
needless repetition and to find more practical data types. I will
not add any more documentation until I have done this, so I'm afraid
out will have to read the source code to learn how to use it.

For now, this is mainly an excercise in API design and a way for me to
play around with interesting Python data types, but if it turns out
well, I will use it to write a patch librarian for my synths, and
perhaps some other toys.

Todo:

   - MIDI channels are numbered 1-16 in user interfaces, but are
     numbered 0-15 in the protocol. Which version should midi.py show?
   - include some kind of event based scheduler (perhaps based on
     http://github/olemb/gametime)
   - include useful lookup tables and functions for common things like
     scales and controller types
   - read and write MIDI files?
   - serialize messages to text files::

    #
    # The first column is relative time in seconds (how long to wait before
    # sending the message.)
    #
    # Omitted columns are filled in with default values.
    #
    0     note_on 2 60 61  # channel 2, note 60 (middle C), velocity=61
    0.1   note_off 2 60 30
    0     note_on 72 2  # will get velocity=127
    0.1   note_off 2 72  # will get veloctiy=127  # (release velocity)
    0     note_on 2 72
    0.1   note_off 2 72

Author: Ole Martin Bjørndalen - ombdalen@gmail.com - http://nerdly.info/ole/

License: MIT
