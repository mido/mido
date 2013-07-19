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
song_select     song
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


Parameter Types
----------------

========  ======================  ================
Name      Valid Range             Default Value
========  ======================  ================
channel   0..15                   0
control   0..127                  0
note      0..127                  0
program   0..127                  0
song      0..127                  0
value     0..127                  0
velocity  0..127                  0
data      (0..127, 0..127, ...)   () (empty tuple)
pitch     -8192..8191             0
pos       0..16383                0
time      any integer or float    0
========  ======================  ================

`velocity` for `note_off` is release velocity, that is how quickly the
note was released. Few instruments support this.

The `time` parameter is not included in the encoded message, and is
(currently) not used by Mido in any way. You can use it for whatever
purpose you wish.

The `data` parameter accepts any iterable that generates numbers in
0..127. This includes::

    mido.Message('sysex', data=[1, 2, 3])
    mido.Message('sysex', data=range(10))
    mido.Message('sysex', data=(i for i in range(10) if i % 2 == 0))

For details about the binary encoding of MIDI message, see:

http://www.midi.org/techspecs/midimessages.php
