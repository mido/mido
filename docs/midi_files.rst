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
messages set to its delta time (in ticks). (See Tempo and Beat
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

You can play back a MIDI file with the play() method::

    for message in mid.play():
        output.send(message)

This will yield each message at the appropriate time for playback.

If you also want to receive meta messages, you can pass
``meta_messages=True``. Meta messages can not be sent to ports, so
they need to be filtered out::

    from mido.midifiles import MetaMessage

    for message in mid.play(meta_messages=True):
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

    from mido.midifies import MidiTrack

    with MidiFile() as mid:
        track = MidiTrack()
        tracks.append(track)

        tracks.append(midi.Message('program_change', program=12, time=0))
        tracks.append(midi.Message('note_on', note=64, velocity=64, time=32)
        tracks.append(midi.Message('note_off', note=64, velocity=127, time=32)

        mid.save('new_song.mid')

The ``MidiTrack`` class is a subclass of list, so you can use all the
usual methods.

All messages must be tagged with delta time (in ticks). (A delta time
is how long to wait before the next message.)

If there is no 'end_of_track' message at the end of a track, one will
be written anyway.

A complete example can be found in ``examples/midifiles/``.


File Types
-----------

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
----------------

You can get the total playback time in seconds by accessing the
``length`` property::

   mid.length

This is only supported for type 0 and 1 files. Accessing ``length`` on
a type 2 file will raise ``ValueError``, since it is impossible to
compute the playback time of an asynchronous file.


Meta Messages
--------------

Meta messages behave like normal messages and can be created in the
usual way, for example::

    >>> from mido.midifiles import MetaMessage
    >>> MetaMessage('key_signature', key='C#', mode='major')
    <meta message key_signature key='C#' mode='major' time=0>

You can tell meta messages apart from normal messages with::

    if isinstance(message, MetaMessage):
        ...

or if you know the message type you can use the ``type`` attribute::

    if message.type == 'key_signature':
        ...
    elif message.type == 'note_on':
        ...

Meta messages can not be sent on ports.

For a list of supported meta messages and their attributes, and also
how to implement new meta messages, see :doc:`meta_message_types`.


About the Time Attribute
-------------------------

The ``time`` attribute is used in several different ways:

* inside a track, it is delta time in ticks

* in messages yielded from ``play()``, it is delta time in seconds
  (time elapsed since the last yielded message)

* (only important to implementers) inside certain methods it is
  used for absolute time in ticks or seconds


Tempo and Beat Resolution
--------------------------

Timing in MIDI files is all centered around beats. A beat is the same
as a quarter note.

Tempo is given in microseconds per beat, and beats are divided into
ticks.

The default tempo is 500000 microseconds per beat, which is half a
second per beat or 120 beats per minute. The meta message 'set_tempo'
can be used to change tempo during a song.

Computations::

    beats_per_seconds = 1000000 / tempo
    beats_per_minute = (1000000 / tempo) * 60
    tempo = (60 / beats_per_minute) * 1000000

Examples::

    2 == 1000000 / 500000
    120 == (1000000 / 500000) * 60
    500000 == (60 / 120.0) * 1000000

Each message in a MIDI file has a delta time, which tells how many
ticks has passed since the last message. The length of a tick is
defined in ticks per beat. This value is stored as ``ticks_per_beat``
in the file header and remains fixed throughout the song. It is used
when converting delta times to and from real time.

(Todo: what's the default value?) 

Computations::

    seconds_per_beat = tempo / 1000000.0
    seconds_per_tick = seconds_per_beat / float(ticks_per_beat)
    time_in_seconds = time_in_ticks * seconds_per_tick
    time_in_ticks = time_in_seconds / seconds_per_tick

Examples::

    0.5 == 500000 / 1000000.0
    0.005 == 0.5 / 100    
    1.0 == 200 * 0.005
    200 == 1.0 / 0.005

(Todo: update with default value.)

MidiFile objects have a ``ticks_per_beat`` attribute, while
``message.time`` is used for delta time. Tempo is updated by
``set_tempo`` meta messages.
