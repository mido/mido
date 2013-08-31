Meta Message Types
===================

key_signature
--------------

=========  ==================  ========
Attribute  Values              Default
=========  ==================  ========
key        'C', 'Cb', ...      'C'
mode       'minor' or 'major'  'major'
=========  ==================  ========

[list of valid keys here?]


set_tempo
----------

=========  ==================  ========
Attribute  Values              Default
=========  ==================  ========
tempo      0..0xffffff         500000
=========  ==================  ========

[This is used to blablabla.]

Sequence Number (0x00)
-----------------------

===============  ==============  ======
Attribute          Values           Default
===============  ==============  ======
sequence number    0 - 65536           0
===============  ==============  ======

[The value from this Meta Message is used to determine the sequence number in type 0 and 1 MIDI files; it determines the pattern number in type 2 MIDI files.]

Text (0x01)
-----------------------

==============  ==============  ========
Attribute          Values        Default
==============  ==============  ========
text              string            ''
==============  ==============  ========

[This Meta Message is a general "Text" Meta Message. It can be used for any text-based data.]

Copyright (0x02)
-----------------------

==============  ==============  ========
Attribute          Values        Default
==============  ==============  ========
text              string            ''
==============  ==============  ========

[This Meta Message will provide information about a MIDI file's copyright.]

Track Name (0x03)
-----------------------

==============  ==============  ========
Attribute          Values        Default
==============  ==============  ========
name              string            ''
==============  ==============  ========

[This Meta Message is used to store a MIDI track's name.]

Instrument Name (0x04)
-----------------------

==============  ==============  ========
Attribute          Values        Default
==============  ==============  ========
name              string            ''
==============  ==============  ========

[This Meta Message is used to store an instrument's name.]



class MetaSpec_lyrics(MetaSpec_text):
    type_byte = 0x05

class MetaSpec_marker(MetaSpec_text):
    type_byte = 0x06

class MetaSpec_cue_marker(MetaSpec_text):
    type_byte = 0x07


