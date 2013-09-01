Meta Message Types
===================

sequence_number (0x00)
-----------------------

===============  ============  ========
Attribute        Values        Default
===============  ============  ========
number           0..65536      0
===============  ============  ========

Determines the sequence number in type 0 and 1 MIDI files;
determines the pattern number in type 2 MIDI files.

text (0x01)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

General "Text" Meta Message. Can be used for any text-based data.

copyright (0x02)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Provides information about a MIDI file's copyright.

track_name (0x03)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Stores a MIDI track's name.

instrument_name (0x04)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Store an instrument's name.

lyrics (0x05)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Stores the lyrics of a song. Typically one syllable per Meta Message.

marker (0x06)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Marks a point of interest in a MIDI file. 
Can be used as the marker for the beginning of a verse, solo, etc.

cue_marker (0x07)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
text            string          ''
==============  ==============  ========

Marks a cue. IE: 'Cue performer 1', etc

device_name (0x09)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
name            string          ''
==============  ==============  ========

Gives the name of the device.

channel_prefix (0x20)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
channel         0..255          0
==============  ==============  ========

Gives the prefix for the channel on which events are played.

midi_port (0x21)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
port            0..255          0
==============  ==============  ========

Gives the MIDI Port on which events are played.

end_of_track (0x2f)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
n/a             n/a             n/a
==============  ==============  ========

An empty Meta Message that marks the end of a track.

set_tempo (0x51)
-----------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
tempo           0..16777215     500000
==============  ==============  ========

Contains the number of microseconds per quarter note.

smpte_offset (0x54)
-----------------------

==============  =================  ========
Attribute       Values             Default
==============  =================  ========
frame_rate      24, 25, 29.97, 30  24
hours           0..23			   0
minutes         0..59			   0
seconds         0..59			   0
frames          0..29			   0
sub_frames      0..99			   0
==============  =================  ========

time_signature (0x58)
-----------------------

============================  	==============  ========
Attribute       				Values          Default
============================  	==============  ========
numerator       				0..255          4
denominator     				1..2**255		2
clocks_per_click    			0..255     		24
notated_32nd_notes_per_beat     0..255			8
============================  	==============  ========

Time signature of:
4/4 : MetaMessage('time_signature', numerator=4, denominator=4)
3/8 : MetaMessage('time_signature', numerator=3, denominator=8)


key_signature (0x59)
-----------------------

=========  ==================  ========
Attribute  Values              Default
=========  ==================  ========
key        'C', 'Cb', ...      'C'
mode       'minor' or 'major'  'major'
=========  ==================  ========

sequencer_specific (0x7f)
--------------------------

==============  ==============  ========
Attribute       Values          Default
==============  ==============  ========
data            [..]			[]
==============  ==============  ========

An unprocessed sequencer specific message containing raw data.

Unknown Meta Messages
----------------------------

In the event that there is an unimplemented MetaMessage type,
it will be returned as an UnknownMetaMessage object.

This object takes the following form:
<unknown meta message 0x## _data=[...], time=0>
and has the attributes:
type = 'unknown meta', _type_byte = '0x##', and _data = [...]