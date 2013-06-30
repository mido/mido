Message Types
==============

==============  ==============================
Name            Keyword Arguments / Attributes
==============  ==============================
note_off        channel note velocity
note_on         channel note velocity
polytouch       channel note value
control_change  channel control value
program_change  channel program
aftertouch      channel value
pitchwheel      channel pitch
sysex           data
undefined_f1
songpos         pos
song            song
undefined_f4
undefined_f5
tune_request
sysex_end
clock
undefined_f9
start
continue
stop
undefined_fd
active_sensing
reset
==============  ==============================


Value Types
------------

========  ======================
Name      Valid Range
========  ======================
channel   0..15
control   0..127
note      0..127
program   0..127
song      0..127
value     0..127
velocity  0..127
data      (0..127, 0..127, ...)
pitch     -8192..8191
pos       0..16383
========  ======================


For details about the binary encoding of MIDI message, see
http://www.midi.org/techspecs/midimessages.php
