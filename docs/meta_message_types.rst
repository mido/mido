Meta Message Types
==================

Supported Messages
------------------

sequence_number (0x00)
^^^^^^^^^^^^^^^^^^^^^^

===============  ============  ========
Attribute        Values        Default
===============  ============  ========
number           0..65535      0
===============  ============  ========

Sequence number in type 0 and 1 MIDI files;
pattern number in type 2 MIDI files.


text (0x01)
^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

General "Text" Meta Message. Can be used for any text based data.


copyright (0x02)
^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Provides information about a MIDI file's copyright.


track_name (0x03)
^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Stores a MIDI track's name.


instrument_name (0x04)
^^^^^^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Stores an instrument's name.


lyrics (0x05)
^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Stores the lyrics of a song. Typically one syllable per Meta Message.


marker (0x06)
^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Marks a point of interest in a MIDI file.
Can be used as the marker for the beginning of a verse, solo, etc.


cue_marker (0x07)
^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Marks a cue. IE: 'Cue performer 1', etc


device_name (0x09)
^^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Gives the name of the device.


channel_prefix (0x20)
^^^^^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
channel         0..255          0
==============  ==============  ========

Gives the prefix for the channel on which events are played.


midi_port (0x21)
^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
port            0..255          0
==============  ==============  ========

Gives the MIDI Port on which events are played.


end_of_track (0x2f)
^^^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
n/a             n/a             n/a
==============  ==============  ========

An empty Meta Message that marks the end of a track.


set_tempo (0x51)
^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
tempo           0..16777215     500000
==============  ==============  ========

Tempo is in microseconds per beat (quarter note). You can use
:py:func:`bpm2tempo` and :py:func:`tempo2bpm` to convert to and from
beats per minute. Note that :py:func:`tempo2bpm` may return a floating
point number.


smpte_offset (0x54)
^^^^^^^^^^^^^^^^^^^

==============  =================  ========
Attribute       Values             Default
==============  =================  ========
frame_rate      24, 25, 29.97, 30  24
hours           0..255             0
minutes         0..59              0
seconds         0..59              0
frames          0..255             0
sub_frames      0..99              0
==============  =================  ========


time_signature (0x58)
^^^^^^^^^^^^^^^^^^^^^

============================  ===============  ========
Attribute                        Values          Default
============================  ===============  ========
numerator                        0..255           4
denominator                      1..2**255        4
clocks_per_click                 0..255           24
notated_32nd_notes_per_beat      0..255           8
============================  ===============  ========

Time signature of:

4/4 : MetaMessage('time_signature', numerator=4, denominator=4)

3/8 : MetaMessage('time_signature', numerator=3, denominator=8)

.. note:: From 1.2.9 time signature message have the correct default
          value of 4/4. In earlier versions the default value was 2/4
          due to a typo in the code.


key_signature (0x59)
^^^^^^^^^^^^^^^^^^^^

=========  ==================  ========
Attribute  Values              Default
=========  ==================  ========
key        'C', 'F#m', ...     'C'
=========  ==================  ========

Valid values: A A#m Ab Abm Am B Bb Bbm Bm C C# C#m Cb Cm D D#m Db Dm E
Eb Ebm Em F F# F#m Fm G G#m Gb Gm

Note: the mode attribute was removed in 1.1.5. Instead, an 'm' is
appended to minor keys.


sequencer_specific (0x7f)
^^^^^^^^^^^^^^^^^^^^^^^^^

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
data            [..]			[]
==============  ==============  ========

An unprocessed sequencer specific message containing raw data.


Unknown Meta Messages
---------------------

Unknown meta messages will be returned as ``UnknownMetaMessage``
objects, with ``type`` set to ``unknown_meta``. The messages are saved
back to the file exactly as they came out.

Code that depends on ``UnknownMetaMessage`` may break if the message
in question is ever implemented, so it's best to only use these to
learn about the format of the new message and then implement it as
described below.

``UnknownMetaMessage`` have two attributes::

    ``type_byte`` - a byte which uniquely identifies this message type
    ``data`` - the message data as a list of bytes

These are also visible in the ``repr()`` string::

    <unknown meta message type_byte=0x## data=[...], time=0>


Implementing New Meta Messages
------------------------------

If you come across a meta message which is not implemented, or you
want to use a custom meta message, you can add it by writing a new
meta message spec::

    from mido.midifiles import MetaSpec, add_meta_spec

    class MetaSpec_light_color(MetaSpec):
        type_byte = 0xf0
        attributes = ['r', 'g', 'b']
        defaults = [0, 0, 0]

    def decode(self, message, data):
        # Interpret the data bytes and assign them to attributes.
        (message.r, message.g, message.b) = data

    def encode(self, message):
        # Encode attributes to data bytes and
        # return them as a list of ints.
        return [message.r, message.g, message.b]

    def check(self, name, value):
        # (Optional)
        # This is called when the user assigns
        # to an attribute. You can use this for
        # type and value checking. (Name checking
        # is already done.
        #
        # If this method is left out, no type and
        # value checking will be done.

        if not isinstance(value, int):
            raise TypeError('{} must be an integer'.format(name))

        if not 0 <= value <= 255:
            raise TypeError('{} must be in range 0..255'.format(name))

Then you can add your new message type with::

    add_meta_spec(MetaSpec_light_color)

and create messages in the usual way::

    >>> from mido import MetaMessage
    >>> MetaMessage('light_color', r=120, g=60, b=10)
    <meta message light_color r=120 g=60 b=10 time=0>

and the new message type will now work when reading and writing MIDI
files.

Some additional functions are available::

    encode_string(unicode_string)
    decode_string(byte_list)

These convert between a Unicode string and a list of bytes using the
current character set in the file.

If your message contains only one string with the attribute name
``text`` or ``name``, you can subclass from one of the existing
messages with these attributes, for example::

    class MetaSpec_copyright(MetaSpec_text):
        type_byte = 0x02

    class MetaSpec_instrument_name(MetaSpec_track_name):
        type_byte = 0x04

This allows you to skip everything but ``type_byte``, since the rest
is inherited.

See the existing MetaSpec classes for further examples.
