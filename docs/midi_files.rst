MIDI Files
===========

MidiFile objects can be used to read, write and play back MIDI
files. (Writing is not yet implemented.)


Opening a File
---------------

You can open a file with::

    from mido.midifiles import MidiFile

    mid = MidiFile('song.mid')

This will read all data into memory. The tracks can be found in the
``tracks`` attribute, which is a list where each track is a list of
messages.


Playing Back The File
----------------------

The ``play()`` method can be used to play back the file in its
entirety.  This will generate each message in the file at the
appropriate time for playback, so all you need to do is::

    for message in mid.play():
        output.send(message)

You will not receive meta messages, so it's safe to send these on to
any Mido port.


Track Contents
---------------

Each track is a list of Mido messages. The ``time`` attribute of each
message is the time that has passed since the previous messages (delta
time). The unit is MIDI ticks.


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

Meta messages have a ``type`` attribute, just like normal messages::


Future Plans: Saving a File
----------------------------

This is not yet implemented, but it is planned to be used something
like this::

    with MidiFile() as mid:  # blank MIDI file
        tracks.append([message1, message2])
        mid.save('new_song.mid')

This will require the messages to be stamped with the correct delta
times, and meta messages to be created and inserted at the correct
place in the track. It is up to the application to do this, but the
library may be expanded later to assist with this if it turns out that
it can be done in a general way, and that it is useful.

