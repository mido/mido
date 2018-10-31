MIDI Files
==========

MidiFile objects can be used to read, write and play back MIDI
files.


Opening a File
--------------

You can open a file with::

    from mido import MidiFile

    mid = MidiFile('song.mid')

.. note:: Sysex dumps such as patch data are often stored in SYX files
   rather than MIDI files. If you get "MThd not found. Probably not a
   MIDI file" try ``mido.read_syx_file()``. (See :doc:`syx` for more.)
   
The ``tracks`` attribute is a list of tracks. Each track is a list of
messages and meta messages, with the ``time`` attribute of each
messages set to its delta time (in ticks). (See Tempo and Beat
Resolution below for more on delta times.)

To print out all messages in the file, you can do::

    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            print(msg)

The entire file is read into memory. Thus you can freely modify tracks
and messages, and save the file back by calling the ``save()``
method. (More on this below.)


Iterating Over Messages
-----------------------

Iterating over a ``MidiFile`` object will generate all MIDI messages
in the file in playback order. The ``time`` attribute of each message
is the number of seconds since the last message or the start of the
file.

Meta messages will also be included. If you want to filter them out,
you can do::

    if msg.is_meta:
        ...

This makes it easy to play back a MIDI file on a port (though this simple
implementation is subject to time drift)::

    for msg in MidiFile('song.mid'):
        time.sleep(msg.time)
        if not msg.is_meta:
            port.send(msg)

This is so useful that there's a method for it::

    for msg in MidiFile('song.mid').play():
        port.send(msg)

This does the sleeping and filtering for you (while avoiding drift). If you
pass ``meta_messages=True`` you will also get meta messages. These can not
be sent on ports, which is why they are off by default.



Creating a New File
-------------------

You can create a new file by calling MidiFile without the ``filename``
argument. The file can then be saved by calling the ``save()`` method::

    from mido import Message, MidiFile, MidiTrack

    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    track.append(Message('program_change', program=12, time=0))
    track.append(Message('note_on', note=64, velocity=64, time=32))
    track.append(Message('note_off', note=64, velocity=127, time=32))
    
    mid.save('new_song.mid')

The ``MidiTrack`` class is a subclass of list, so you can use all the
usual methods.

All messages must be tagged with delta time (in ticks). (A delta time
is how long to wait before the next message.)

If there is no 'end_of_track' message at the end of a track, one will
be written anyway.

A complete example can be found in ``examples/midifiles/``.

The ``save`` method takes either a filename (``str``) or, using the ``file``
keyword parameter, a file object such as an in-memory binary file (an
``io.BytesIO``). If you pass a file object, ``save`` does not close it.
Similarly, the ``MidiFile`` constructor can take either a filename, or
a file object by using the ``file`` keyword parameter. if you pass a file
object to ``MidiFile`` as a context manager, the file is not closed when
the context manager exits. Examples can be found in ``test_midifiles2.py``.



File Types
----------

There are three types of MIDI files:

* type 0 (single track): all messages are saved in one track
* type 1 (synchronous): all tracks start at the same time
* type 2 (asynchronous): each track is independent of the others

When creating a new file, you can select type by passing the ``type``
keyword argument, or by setting the ``type`` attribute::

   mid = MidiFile(type=2)
   mid.type = 1

Type 0 files must have exactly one track. A ``ValueError`` is raised
if you attempt to save a file with no tracks or with more than one
track.


Playback Length
---------------

You can get the total playback time in seconds by accessing the
``length`` property::

   mid.length

This is only supported for type 0 and 1 files. Accessing ``length`` on
a type 2 file will raise ``ValueError``, since it is impossible to
compute the playback time of an asynchronous file.


Meta Messages
-------------

Meta messages behave like normal messages and can be created in the
usual way, for example::

    >>> from mido import MetaMessage
    >>> MetaMessage('key_signature', key='C#', mode='major')
    <meta message key_signature key='C#' mode='major' time=0>

You can tell meta messages apart from normal messages with::

    if msg.is_meta:
        ...

or if you know the message type you can use the ``type`` attribute::

    if msg.type == 'key_signature':
        ...
    elif msg.type == 'note_on':
        ...

Meta messages can not be sent on ports.

For a list of supported meta messages and their attributes, and also
how to implement new meta messages, see :doc:`meta_message_types`.


About the Time Attribute
------------------------

The ``time`` attribute is used in several different ways:

* inside a track, it is delta time in ticks. This must be an integer.

* in messages yielded from ``play()``, it is delta time in seconds
  (time elapsed since the last yielded message)

* (only important to implementers) inside certain methods it is
  used for absolute time in ticks or seconds


Tempo and Beat Resolution
-------------------------

.. image:: images/midi_time.svg

Timing in MIDI files is centered around ticks and beats. A beat is the same as 
a quarter note. Beats are divided into ticks, the smallest unit of time in 
MIDI.

Each message in a MIDI file has a delta time, which tells how many ticks have 
passed since the last message. The length of a tick is defined in ticks per 
beat. This value is stored as ``ticks_per_beat`` in MidiFile objects and 
remains fixed throughout the song.


MIDI Tempo vs. BPM
^^^^^^^^^^^^^^^^^^

Unlike music, tempo in MIDI is not given as beats per minute, but rather in 
microseconds per beat.

The default tempo is 500000 microseconds per beat, which is 120 beats per 
minute. The meta message 'set_tempo' can be used to change tempo during a song.

You can use :py:func:`bpm2tempo` and :py:func:`tempo2bpm` to convert to and 
from beats per minute. Note that :py:func:`tempo2bpm` may return a floating 
point number.

Converting Between Ticks and Seconds
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To convert from MIDI time to absolute time in seconds, the number of beats per 
minute (BPM) and ticks per beat (often called pulses per quarter note or PPQ, 
for short) have to be decided upon.

You can use :py:func:`tick2second` and :py:func:`second2tick` to convert to
and from seconds and ticks. Note that integer rounding of the result might be 
necessary because MIDI files require ticks to be integers.

If you have a lot of rounding errors you should increase the time resolution 
with more ticks per beat, by setting MidiFile.ticks_per_beat to a large number.
Typical values range from 96 to 480 but some use even more ticks per beat.

