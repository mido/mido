MIDI Files
===========

MidiFile objects can be used to read, write and play back MIDI
files. (Writing is not yet implemented.)


Opening a File
---------------

You can open a file with::

    from mido.midifiles import MidiFile

    mid = MidiFile('song.mid')

The ``tracks`` attribute is a list of tracks. Each track is a list of
messages and meta messages, with the ``time`` attribute of each
messages set to its delta time (in ticks). (See Tempo and Time
Resolution below for more on delta times.)

To print out all messages in the file, you can do::

    for i, track in enumerate(mid.tracks):
        print('Track {}: {}'.format(i, track.name))
        for message in track:
            print(message)

The entire file is read into memory. Thus you can freely modify tracks
and messages, and save the file back by calling the ``save()``
method. (More on this below.)


Playing Back The File
----------------------

You can play back a MIDI file by iterating over it and sending the
messages to a port. The generator will call ``time.sleep()`` before
each messages is yielded, so you get them at the correct time::

    for message in mid:
        output.send(message)

The ``time`` attribute will be set to delta time (the number of
seconds slept before the message was yielded).

If you also want to receive meta messages, you can call the ``play()``
method directly. Meta messages can not be sent to ports, so they need
to be filtered out::

    from mido.midifiles import MetaMessage

    for message in mid:
        if isinstance(message, MetaMessage):
            print('Got meta message', MetaMessage)
        else:
            output.send(message)


Creating a New File
--------------------

*Note*: Saving of meta messages other than 'end_of_track' is not yet
 implemented. (They will simply be skipped, which will most likely
 mess up timing.)

You can create a new file by calling MidiFile without the ``filename``
argument. The file can then be saved by calling the ``save()`` method::

    from mido.midifies import Track

    with MidiFile() as mid:
        track = Track()
        tracks.append(track)

        tracks.append(midi.Message('program_change', program=12, time=0))
        tracks.append(midi.Message('note_on', note=64, velocity=64, time=32)
        tracks.append(midi.Message('note_off', note=64, velocity=127, time=32)

        mid.save('new_song.mid')

The ``Track`` class is a subclass of list, so you can use all the
usual methods.

All messages must be tagged with delta time (in ticks). (A delta time
is how long to wait before the next message.)

If there is no 'end_of_track' message at the end of a track, one will
be written anyway.

A complete example can be found in ``examples/midifiles/``.


File Formats
-------------

MIDI files have three different formats:

* format 0 (single track): all messages are saved in one track
* format 1 (synchronous): all tracks start at the same time
* format 2 (asynchronous): each track is independent of the others

You can select file format by passing the ``format`` keyword argument,
or by setting the ``format`` attribute::

   mid = MidiFile(format=2)
   mid.format = 1

Format 0 files must have exactly one track. A ``ValueError`` is raised
if you attempt to save a file with no tracks or with more than one
track.


Meta Messages
--------------

In addition to normal messages, MIDI files contain meta messages.
These are used to set things like tempo, time signature, key
signature and track name::

    >>> meta = MetaMessage('track_name', name='Just Another Track', time=222)
    >>> meta.type
    'track_name'
    >>> meta.hex()
    'FF 03 12 4A 75 73 74 20 41 6E 6F 74 68 65 72 20 54 72 61 63 6B'

Both message types are subclassed from ``BaseMessage``. You can tell
them apart by their class, so for example to filter out the meta
messages from a track, you can do::

    messages = [m for m in track if not isinstance(m, MetaMessage)]

Meta messages are only found in MIDI files and can not be sent to
ports.


Tempo and Time Resolution
--------------------------

(Todo: write about the tempo message when it has
been implemented.)

(Todo: exmplain ticks.)

You can adjust the resolution of time ticks by setting this attribute::

   mid.ticks_per_quarter_note = 360

This will affect playback tempo, so you need to adjust the ``tempo``
messages accordingly.
